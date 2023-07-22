import google.generativeai as palm
try:
    from chat_agent.LLMs.chat_base import ChatBase
except:
    from LLMs.chat_base import ChatBase


class ChatModel(ChatBase):
    def __init__(self, config):
        super(ChatModel, self).__init__(config)
        palm.configure(api_key=self.api_key)

    def complete(self, prompt):
        prompt = self.convert_prompts(prompt)
        response = palm.chat(
            model=self.config['model'],
            context=prompt[0]['content'],
            messages=prompt[1:],
            temperature=self.config.get('temperature', 0),
            top_p=self.config.get('top_p', 1)
        )
        return response.last
    
    def convert_prompts(self, prompt):
        palm_prompts = [{'author': p['role'], 'content': p['content']} for p in prompt]
        return palm_prompts

