import os
import sys
import logging
import json
from datetime import datetime
from dotenv import load_dotenv

# speech recognition and synthesis
try:
    from openai_chat_agent.voice.vosk_recognizer import SpeechRecognize
    from openai_chat_agent.voice.tts import Text2Speech
    from openai_chat_agent.utils.context import Context
    from openai_chat_agent.utils.google_search import GoogleSearch
    from openai_chat_agent.utils.chat_openai import ChatOpenAI
except:
    from voice.vosk_recognizer import SpeechRecognize
    from voice.tts import Text2Speech
    from utils.context import Context
    from utils.google_search import GoogleSearch
    from utils.chat_openai import ChatOpenAI


class ChatAgent:
    debug = True

    def __init__(self, verbose=False):
        self.verbose = verbose
        load_dotenv()

        # setup logging
        now = datetime.now()
        logfile = f'chatlog-{now.strftime("%m.%d.%Y-%H.%M.%S")}.log'
        logpath = os.path.join('openai_chat_agent', 'logs', logfile)
        logging.basicConfig(handlers=[logging.FileHandler(logpath, 'w', 'utf-8')], 
                            level=logging.INFO, 
                            format='%(asctime)s %(message)s')
        self.logger = logging.getLogger('chat_log')

        # setup chat logging (transcript)
        self.chat_logger = ChatLogging()

        # fetch profile
        profile_path = os.path.join('openai_chat_agent', 'user_profile.txt')
        with open(profile_path, 'r') as FILE:
           user_profile = FILE.read()

        # And template for search result prompts
        template_path = os.path.join('openai_chat_agent', 'result_prompt.txt')
        with open(template_path, 'r') as FILE:
            self.result_template = FILE.read()

        # setup sys prompt
        prompt_path = os.path.join('openai_chat_agent', 'sys_prompt.txt')
        with open(prompt_path, 'r') as FILE:
           sys_prompt = FILE.read()
        sys_prompt = sys_prompt.replace('``user_profile```', user_profile)

        # setup chat model and memory
        self.chat = ChatOpenAI()
        self.context = Context(sys_prompt)
        
        # setup search tool
        self.search=GoogleSearch(verbose=verbose)

    def __call__(self, text):
        self.logger.info(f'User\'s message: {text}')
        self.chat_logger.log_message(f'Human: {text}')
        done = False
        while not done:
            self.context.add(role='user', text=text)
            prompt = self.context.get_prompt()
            output = self.chat(prompt)
            try:
                result = json.loads(output)
            except:
                result = {'action': 'final', 'content': str(output)}
            self.logger.info(str(result))

            if self.verbose:
                print(result)
            action = result.get('action')
            content = result.get('content')
            try:
                content_json = json.loads(content)
                content = content_json['content']
            except:
                pass
            links = None

            if action == 'final':
                reply = content
                done = True
            elif action == 'search':
                summary, links = self.search(content)
                text = self.result_template.replace('```summary```', summary)
                text = text.replace('```query```', text)
                self.context.add(role='assistant', text=str(result)) 
        self.chat_logger.log_message(f'AI: {reply}') 
        return reply, links
        

class ChatLogging:
    def __init__(self):
        now = datetime.now()
        chat_file = f'chat-{now.strftime("%m.%d.%Y-%H.%M.%S")}.log'
        self.chat_path = os.path.join('openai_chat_agent', 'chats', chat_file)

    def log_message(self, message):
        with open(self.chat_path, 'a') as FILE:
            FILE.write(f'{message}\n\n')        


class Bot:
    def __init__(self, voice=False, verbose=False):
        self.recog = SpeechRecognize()
        self.tts = Text2Speech()
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
