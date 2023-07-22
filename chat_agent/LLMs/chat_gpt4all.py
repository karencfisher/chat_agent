from gpt4all import GPT4All
try:
    from chat_agent.LLMs.chat_base import ChatBase
except:
    from LLMs.chat_base import ChatBase


class ChatModel(ChatBase):
    def __init__(self, config):
        super(ChatModel, self).__init__(config)
        self.gpt4all = GPT4All(self.config['model'])

    def complete(self, prompt):
        response =  self.gpt4all.chat_complete(
            messages=prompt,
            verbose=False,
            streaming=False
        )
        text = response['choices'][0]['message']['content']
        return text
