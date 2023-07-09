import json
from gpt4all import GPT4All
import logging
from dotenv import load_dotenv


class ChatDummy:
    def __init__(self, config):
        self.logger = logging.getLogger('chat_log')
        self.logger.info(f'Using configuration {config}')

    def __call__(self, prompt):
        output = {'action': 'final', 'content': "{'action': 'final', 'content': 'this is just a test'}"}
        return json.dumps(output)
