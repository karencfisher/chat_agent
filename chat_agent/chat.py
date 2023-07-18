import os
import sys
import logging
import json
import re
import importlib
import datetime
from dotenv import load_dotenv

# speech recognition and synthesis
try:
    from chat_agent.memory.context import Context
except:
    from memory.context import Context


class ChatAgent:
    debug = True

    def __init__(self, verbose=False):
        self.verbose = verbose
        load_dotenv()

        # setup logging
        now = datetime.datetime.now()
        logfile = f'chatlog-{now.strftime("%m.%d.%Y-%H.%M.%S")}.log'
        logpath = os.path.join('chat_agent', 'logs', logfile)
        logging.basicConfig(handlers=[logging.FileHandler(logpath, 'w', 'utf-8')], 
                            level=logging.INFO, 
                            format='%(asctime)s %(message)s')
        self.logger = logging.getLogger('chat_log')

        # setup chat logging (transcript)
        self.chat_logger = ChatLogging()

        # setup chat model
        config_path = os.path.join('chat_agent', 'chat_config.json')
        with open(config_path, 'r') as FILE:
            config = json.load(FILE)
        try:
            provider = importlib.import_module('chat_agent.LLMs.' + config['provider'].strip())
        except:
            provider = importlib.import_module('LLMs.' + config['provider'].strip())
        self.chat = provider.ChatModel(config)
        
        # setup tools
        tools_path = os.path.join('chat_agent', 'tools.json')
        with open(tools_path, 'r') as FILE:
           tools = json.load(FILE)

        self.tools = {}
        tool_descriptions = []
        for tool in tools:
            try:
                module = importlib.import_module('chat_agent.tools.' +  tool['module'])
            except:
                module = importlib.import_module('tools.' +  tool['module'])
            object = module.Tool(tool['name'], **tool['parameters'])
            self.tools[tool['name']] = object
            tool_descriptions.append(f'{tool["name"]}: {tool["description"]}')

        # setup sys prompt
        prompt_path = os.path.join('chat_agent', 'sys_prompt.txt')
        with open(prompt_path, 'r') as FILE:
           sys_prompt = FILE.read()

        sys_prompt = sys_prompt.format(
                today = datetime.date.today(),
                tool_description='\n'.join(tool_descriptions),
                tool_names=', '.join(list(self.tools.keys())))
        
        # context buffer
        self.context = Context(sys_prompt, 
                               num_response_tokens=config['max_tokens'],
                               max_context_tokens=config['max_context'])

    def __call__(self, text):
        self.logger.info(f'User\'s message: {text}')
        self.chat_logger.log_message(f'Human: {text}')
        done = False
        while not done:
            self.context.add(role='user', text=text)
            prompt = self.context.get_prompt()
            output = self.chat(prompt)
            self.logger.info(f'AI: {output}')
            if self.verbose:
                print(output)

            tool, tool_input = self.__parse(output)
            if tool == 'Final Answer':
                done = True
                metadata = None
                continue
            if tool not in list(self.tools.keys()):
                raise KeyError('Invalid tool name')
            
            result, metadata = self.tools['tool'](tool_input)
            if metadata is not None:
                try:
                    self.tools['tool'].post_process(metadata)
                except:
                    pass

            text = f'Observation: {result}\n' + text
                        
        self.chat_logger.log_message(f'AI: {tool_input}') 
        return tool_input, metadata
    
    def __parse(self, generated: str):
        if 'Final Answer:' in generated:
            return "Final Answer", generated.split('Final Answer:')[-1].strip()
        regex = r"Action: [\[]?(.*?)[\]]?[\n]*Action Input:[\s]*(.*)"
        match = re.search(regex, generated, re.DOTALL)
        if not match:
            tool = 'Final Answer'
            tool_input = generated
        else:
            tool = match.group(1).strip()
            tool_input = match.group(2)
        return tool, tool_input.strip(" ").strip('"')
        

class ChatLogging:
    def __init__(self):
        now = datetime.datetime.now()
        chat_file = f'chat-{now.strftime("%m.%d.%Y-%H.%M.%S")}.log'
        self.chat_path = os.path.join('chat_agent', 'chats', chat_file)

    def log_message(self, message):
        with open(self.chat_path, 'a') as FILE:
            FILE.write(f'{message}\n\n')        


class Bot:
    def __init__(self, voice=False, verbose=False):
        if voice:
            # initialize voice functions
            print('Initializing speech...')
            try:
                from chat_agent.voice.vosk_recognizer import SpeechRecognize
                from chat_agent.voice.tts import Text2Speech
            except:
                from voice.vosk_recognizer import SpeechRecognize
                from voice.tts import Text2Speech

            self.recog = SpeechRecognize()
            self.tts = Text2Speech()
            print('Done')
        
        self.voice = voice
        self.chat_agent = ChatAgent(verbose=verbose)

    def loop(self):
        # start loop
        text = 'hello'
        while True:
            result, _ = self.chat_agent(text)
            if self.voice:
                print('\rtalking...     ', end='')
                self.tts.speak(result)
            else:
                print(f'\nAI: {result}\n')

            if text.lower() == 'goodbye':
                break

            if self.voice:
                print('\rlistening...     ', end='')
                text = self.recog.speech_to_text()
            else:
                text = input('Human: ')
                
        print('\ndone!')


def main():
    params = {'voice': False, 'verbose': False}
    if len(sys.argv) > 1:
        print(list(sys.argv))
        for arg in sys.argv[1:]:
            if arg in params.keys():
                params[arg] = True
            else:
                raise ValueError('Invalid command line argument {sys.argv[1]}')
    bot = Bot(voice=params['voice'], 
              verbose=params['verbose'])
    bot.loop()

if __name__ == '__main__':
    main()
