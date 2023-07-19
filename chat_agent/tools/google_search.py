import requests
from bs4 import BeautifulSoup
import os
import numpy as np
import asyncio
import openai
import time
import logging

from dotenv import load_dotenv
from collections import defaultdict
from fake_useragent import UserAgent

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

try:
    from chat_agent.tools.async_web_scraper import AsyncWebScraper
    from chat_agent.tools.base_tool import BaseTool
except:
    from tools.async_web_scraper import AsyncWebScraper
    from tools.base_tool import BaseTool


class Tool(BaseTool):
    def __init__(self, tool_name, **kwargs):
        super(Tool, self).__init__(tool_name=tool_name, tool_object=self)
        self.num_search = kwargs.get('num_search', 10)
        self.k_best = kwargs.get('k_best', 5)
        self.l2_threshold = kwargs.get('l2_threshold', 0.4)
        self.verbose = kwargs.get('verbose', False)
        self.db = None

        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_cx = os.getenv('GOOGLE_CSE_ID')

        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)

    def __get_pages(self, query):
        if self.verbose:
            print(f'Searching the web for {self.num_search} websites on \"{query}\"')

        # call Google custom search engine to find websites
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {"key": self.google_api_key,
                  "cx": self.google_cx,
                  "q": query,
                  "num": self.num_search}
        response = requests.get(url, params)

        if response.status_code != 200:
            return [{"error_response": response.status_code}]
        return response.json()['items']
    
    async def __get_documents_async(self, items):
        if self.verbose:
            print('Fetching pages and breaking into chunks')

        scraper = AsyncWebScraper(self.text_splitter)
        docs = await scraper.get_documents(items)

        if self.verbose:
            print('')
        return docs
    
    def __get_documents(self, items):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.__get_documents_async(items))
    
    def __store_documents(self, docs):
        # vectorize documents and select best k_best
        if self.verbose:
            print(f'Create and load documents to vector DB')
        if self.db is None:
            self.db = FAISS.from_documents(documents=docs, embedding=self.embeddings)
        else:
            temp_db = FAISS.from_documents(documents=docs, embedding=self.embeddings)
            self.db.merge_from(temp_db)

    def __get_selections(self, query):
        if self.verbose:
            print('Semantic search on vector DB')
        # vectorize documents and select best k_best
        selections = self.db.similarity_search_with_score(query, k=self.k_best)
        self.logger.info(f'Relevant documents: {selections}')
        if self.verbose:
            print(f'The relevant documents I found:')
            for selection in selections:
                print(selection)
            print('')
        return selections
    
    def __get_summary(self, selections):
        if self.verbose:
            print('Summarizing findings.')
        # get references used, in ranked order
        hash = defaultdict(int)
        for selection in selections:
            hash[selection[0].metadata['reference']] += 1
        counts = [(k, v) for k, v in hash.items()]
        counts.sort(key=lambda x: x[1], reverse=True)
        references = [link for link, _ in counts]

        # have LMM summarize extracted information
        prompt = f'Write a detailed summary of the following information: {selections}'
        summary = openai.ChatCompletion.create(model='gpt-3.5-turbo',
                                    messages=[{'role': 'user', 'content': prompt}],
                                    temperature=0)
        if self.verbose:
            print(f'Summary: {summary.choices[0].message.content}\nReferences: {references}')
        return (summary.choices[0].message.content, references)
    
    def __call__(self, query, tool_queue):
        # if we have data, see if query is valid for it
        if self.db is not None:
            if self.verbose:
                selections = self.__timeit(self.__get_selections, (query,))
            else:
                selections = self.__get_selections(query)
            # if distance < threshold, we can use those results
            if selections[0][1] < self.l2_threshold:
                self.logger.info('Found relevant documents in cache.')
                if self.verbose:
                    print('Re-using previous search data')
                    return self.__timeit(self.__get_summary, (selections,))
                tool_queue.put(self.__get_summary(selections))
                return
            else:
                self.logger.info('No relevant documents in cache, searching for more.')
                if self.verbose:
                    print('Previous data is not sufficient, so I have to search again.')
                
        # if not, we perform a new search
        if self.verbose:
            overall_start = time.time()

            items = self.__timeit(self.__get_pages, (query,))      
            docs = self.__timeit(self.__get_documents, (items,))
            self.__timeit(self.__store_documents, (docs,))
            selections = self.__timeit(self.__get_selections, (query,))
            output = self.__timeit(self.__get_summary, (selections,))
            
            overall_elapsed = time.time() - overall_start
            print(f'Total elapsed time = {overall_elapsed: .3f}')
        else:
            items = self.__get_pages(query)       
            docs = self.__get_documents(items)
            self.__store_documents(docs)
            selections = self.__get_selections(query)
            output = self.__get_summary(selections)
        tool_queue.put(output)
    
    def __timeit(self, func, args):
        start = time.time()
        output = func(*args)
        elapsed = time.time() - start
        print(f'elapsed time current step = {elapsed: .3f}')
        return output

