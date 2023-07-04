import requests
import json
from bs4 import BeautifulSoup
import re
import os
import numpy as np
import faiss
from dotenv import load_dotenv
from collections import defaultdict
from fake_useragent import UserAgent

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

import openai


class GoogleSearch:
    def __init__(self, num_search=10, k_best=5, verbose=False):
        self.num_search = num_search
        self.k_best = k_best
        self.verbose = verbose

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
    
    def __get_documents(self, items):
        if self.verbose:
            print('Fetching pages and breaking into chunks')
        links = []
        docs = []
        for index, item in enumerate(items):
            links.append({"title": item['title'], "link": item['link']})

            # spoof as a chrome browser and fetch website
            ua = UserAgent
            header = {'User-Agent': str(ua.chrome)}
            article_response = requests.get(item['link'], headers=header)

            # scrape the text
            html_doc = article_response.text
            soup = BeautifulSoup(html_doc, 'html.parser')
            text = soup.get_text().strip()
            text = re.sub(r'\n+', '\n', text)

            # split into documents for semantic search
            docs += self.text_splitter.create_documents([text], 
                                                        metadatas=[{"item": index}])
            
            if self.verbose:
                print(f'\r{len(docs)} documents', end='')
        if self.verbose:
            print('')
        return docs, links
    
    def __get_selections(self, docs, query):
        # vectorize documents and select best k_best
        self.db = FAISS.from_documents(documents=docs, embedding=self.embeddings)
        selections = self.db.similarity_search(query, k=self.k_best)
        if self.verbose:
            print(f'The relevant documents I found:')
            for selection in selections:
                print(selection)
            print('')
        return selections
    
    def __get_summary(self, selections, links):
        # get references used, in ranked order
        hash = defaultdict(int)
        for selection in selections:
            hash[selection.metadata['item']] += 1
        counts = [(k, v) for k, v in hash.items()]
        counts.sort(key=lambda x: x[1], reverse=True)
        references = [links[i] for i, _ in counts]

        # have LMM summarize extracted information
        prompt = f'Write a summary of the following information: {selections}'
        summary = openai.ChatCompletion.create(model='gpt-3.5-turbo',
                                    messages=[{'role': 'user', 'content': prompt}],
                                    temperature=0)
        return summary.choices[0].message.content, references
    
    def __call__(self, query):
        items = self.__get_pages(query)
        docs, links = self.__get_documents(items)
        selections = self.__get_selections(docs, query)
        summary, references = self.__get_summary(selections, links)
        return summary, references
    
