# Thank you to ChatGPT for its assistance!
import asyncio
import aiohttp
import logging
import os
from fake_useragent import UserAgent
from datetime import datetime
from bs4 import BeautifulSoup
import re

class AsyncWebScraper:
    def __init__(self, text_splitter, verbose=False):
        self.text_splitter = text_splitter
        self.verbose = verbose
        self.logger = logging.getLogger('chat_log')

    async def process_item(self, session, item):
        ua = UserAgent
        header = {'User-Agent': str(ua.chrome)}
        self.logger.info(f'Requesting {item["link"]}')
        try:
            async with session.get(item['link'], headers=header, timeout=5) as response:
                article_text = await response.text()
                self.logger.info(f'Processing {item["link"]}')
                soup = BeautifulSoup(article_text, 'html.parser')
                text = soup.get_text().strip()
                text = re.sub(r'\n+', '\n', text)
                documents = self.text_splitter.create_documents([text],
                                metadatas=[{'reference': (item['title'], item['link'])}])
                self.logger.info('Successful')
                return documents
        except asyncio.TimeoutError:
            # Handle timeout error here
            await asyncio.to_thread(self.logger.error, f'Request timed out on {item["link"]}')
            return []
        except Exception as e:
            # Log the exception within an asynchronous context
            await asyncio.to_thread(self.logger.error, f'Error occurred: {str(e)}')
        
    async def get_documents(self, items):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for item in items:
                task = asyncio.create_task(self.process_item(session, item))
                tasks.append(task)

            docs = []
            completed = 0
            for task in asyncio.as_completed(tasks):
                documents = await task
                try:
                    docs += documents
                except TypeError:
                    pass
                completed += 1
        return docs
