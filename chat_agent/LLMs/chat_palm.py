import os
import google.generativeai as palm
import logging
from dotenv import load_dotenv


class ChatModel:
    def __init__(self, config):
        load_dotenv()
        palm_api_key = os.getenv('PALM_API_KEY')
        palm.configure(api_key=palm_api_key)

        self.config = config

        self.logger = logging.getLogger('chat_log')
        self.logger.info(f'Using configuration {self.config}')

    def __call__(self, prompt):
        prompt = self.convert_prompts(prompt)
        self.logger.info(f'Prompt: {prompt}')
        response = palm.chat(
            model=self.config['model'],
            context=prompt[0]['content'],
            messages=prompt[1:],
            temperature=self.config['temperature'],
            top_p=self.config['top_p']
        )
        return response.last
    
    def convert_prompts(self, prompt):
        palm_prompts = [{'author': p['role'], 'content': p['content']} for p in prompt]
        return palm_prompts

