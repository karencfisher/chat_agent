import os
import openai
import json
import logging
from dotenv import load_dotenv


class ChatOpenAI:
    def __init__(self):
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')

        config_path = os.path.join('openai_chat_agent', 'utils', 'openai_config.json')
        with open(config_path, 'r') as FILE:
            self.config = json.load(FILE)

        self.logger = logging.getLogger('chat_log')
        self.logger.info(f'Using configuration {self.config}')

    def __call__(self, prompt):
        self.logger.info(f'Prompt: {prompt}')
        result = openai.ChatCompletion.create(
            model=self.config['model'],
            messages = prompt,
            temperature=self.config['temperature'],
            top_p=self.config['top_p'],
            n=self.config["n"],
            presence_penalty=self.config["presence_penalty"],
            frequency_penalty=self.config["frequency_penalty"],
            max_tokens=self.config["max_tokens"]
        )
        return result.choices[0].message.content
