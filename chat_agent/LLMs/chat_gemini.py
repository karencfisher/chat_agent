import google.generativeai as genai
try:
    from chat_agent.LLMs.chat_base import ChatBase
except:
    from LLMs.chat_base import ChatBase


class ChatModel(ChatBase):
    def __init__(self, config):
        super(ChatModel, self).__init__(config)
        genai.configure(api_key=self.api_key)
        model_config = genai.GenerationConfig(
            max_output_tokens=self.config["max_tokens"],
            temperature=self.config["temperature"],
            top_p=self.config["top_p"],
            top_k=self.config["top_k"]
        )
        self.model = genai.GenerativeModel(self.config["model"],
                                           generation_config=model_config)

    def complete(self, prompt):
        prompt = self.convert_prompts(prompt)
        try:
            response = self.model.generate_content(prompt)
        except Exception as ex:
            print(f'Exception: {ex}')
            print(f'Context: {prompt}')
            return "An error occured!"
        return " ".join([part.text for part in response.candidates[0].content.parts])
    
    def convert_prompts(self, prompt):
        parts = [prompt[0]["content"]]
        if len(prompt) > 1:
            parts.append(prompt[1]["content"])
        gemini_prompts = [{"role": "user", "parts": parts}]
        for message in prompt[2:]:
            role = "model" if message["role"] == "assistant" else "user"
            gemini_prompt = {"role": role, "parts": [message["content"]]}
            gemini_prompts.append(gemini_prompt)
        return gemini_prompts

