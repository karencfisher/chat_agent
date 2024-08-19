from groq import Groq
try:
    from chat_agent.LLMs.chat_base import ChatBase
except:
    from LLMs.chat_base import ChatBase


class ChatModel(ChatBase):
    def __init__(self, config):
        super(ChatModel, self).__init__(config)
        self.client = Groq(
            api_key=self.api_key
        )

    def complete(self, prompt):
        result = self.client.chat.completions.create(
            model=self.config['model'],
            messages = prompt
        )
        return result.choices[0].message.content
