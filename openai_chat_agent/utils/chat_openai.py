import os
import openai
from dotenv import load_dotenv


class ChatOpenAI:
    def __init__(self):
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def __call__(self, prompt):
        result = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages = prompt,
            temperature=0
        )
        return result.choices[0].message.content
