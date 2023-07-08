# Thank you to ChatGPT
import asyncio
import aiohttp
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import re

class AsyncWebScraper:
    def __init__(self, text_splitter, verbose=False):
        self.text_splitter = text_splitter
        self.verbose = verbose

    async def fetch_page(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    async def process_item(self, session, item):
        ua = UserAgent
        header = {'User-Agent': str(ua.chrome)}
        async with session.get(item['link'], headers=header) as response:
            article_text = await response.text()
            soup = BeautifulSoup(article_text, 'html.parser')
            text = soup.get_text().strip()
            text = re.sub(r'\n+', '\n', text)
            documents = self.text_splitter.create_documents([text],
                            metadatas=[{'reference': (item['title'], item['link'])}])
            return documents

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
                docs += documents
                completed += 1

                if self.verbose:
                    print(f'\r{completed} documents', end='')

        if self.verbose:
            print('')

        return docs
