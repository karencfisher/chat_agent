import os
import logging
from dotenv import load_dotenv


class ChatBase:
    def __init__(self, config):
        load_dotenv()
        self.api_key = os.getenv(config.get('api_key'))
        self.config = config
        self.logger = logging.getLogger('chat_log')
        self.logger.info(f'Using configuration {self.config}')

    def __call__(self, prompt):
        self.logger.info(f'Prompt: {prompt[-1]}')
        return self.complete(prompt)
    
    def complete(self, prompt):
        raise NotImplementedError('complete method not implemented')
    