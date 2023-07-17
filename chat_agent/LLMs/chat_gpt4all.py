import os
from gpt4all import GPT4All
import logging
from dotenv import load_dotenv


class ChatGPT4ALL:
    def __init__(self, config):
        self.config = config

        self.gpt4all = GPT4All(self.config['model'])

        self.logger = logging.getLogger('chat_log')
        self.logger.info(f'Using configuration {self.config}')

    def __call__(self, prompt):
        self.logger.info(f'Prompt: {prompt}')
        response =  self.gpt4all.chat_complete(
            messages=prompt,
            verbose=False,
            streaming=False
        )
        text = response['choices'][0]['message']['content']
        return text
