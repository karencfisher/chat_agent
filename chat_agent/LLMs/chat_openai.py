import openai
try:
    from chat_agent.LLMs.chat_base import ChatBase
except:
    from LLMs.chat_base import ChatBase


class ChatModel(ChatBase):
    def __init__(self, config):
        super(ChatModel, self).__init__(config)
        openai.api_key = self.api_key

    def complete(self, prompt):
        result = openai.ChatCompletion.create(
            model=self.config['model'],
            messages = prompt,
            temperature=self.config.get('temperature', 0),
            top_p=self.config.get('top_p', 1),
            n=self.config.get('n', 1),
            presence_penalty=self.config.get('presence_penalty', 0),
            frequency_penalty=self.config.get('frequency_penalty', 0),
            max_tokens=self.config['max_tokens']
        )
        return result.choices[0].message.content
