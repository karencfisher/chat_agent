import os
import sys
import logging
import json
from datetime import datetime
from dotenv import load_dotenv

# speech recognition and synthesis
try:
    from chat_agent.utils.context import Context
    from chat_agent.utils.google_search import GoogleSearch
    from chat_agent.utils.chat_openai import ChatOpenAI
    from chat_agent.utils.chat_palm import ChatPalm
except:
    from utils.context import Context
    from utils.google_search import GoogleSearch
    from utils.chat_openai import ChatOpenAI
    from utils.chat_palm import ChatPalm
    from utils.chat_dummy import ChatDummy


class ChatAgent:
    debug = True

    def __init__(self, verbose=False):
        self.verbose = verbose
        load_dotenv()

        # setup logging
        now = datetime.now()
        logfile = f'chatlog-{now.strftime("%m.%d.%Y-%H.%M.%S")}.log'
        logpath = os.path.join('chat_agent', 'logs', logfile)
        logging.basicConfig(handlers=[logging.FileHandler(logpath, 'w', 'utf-8')], 
                            level=logging.INFO, 
                            format='%(asctime)s %(message)s')
        self.logger = logging.getLogger('chat_log')

        # setup chat logging (transcript)
        self.chat_logger = ChatLogging()

        # fetch profile
        profile_path = os.path.join('chat_agent', 'user_profile.txt')
        with open(profile_path, 'r') as FILE:
           user_profile = FILE.read()

        # And template for search result prompts
        template_path = os.path.join('chat_agent', 'result_prompt.txt')
        with open(template_path, 'r') as FILE:
            self.result_template = FILE.read()

        # setup sys prompt
        prompt_path = os.path.join('chat_agent', 'sys_prompt.txt')
        with open(prompt_path, 'r') as FILE:
           sys_prompt = FILE.read()
        sys_prompt = sys_prompt.replace('``user_profile```', user_profile)

        # setup chat model
        config_path = os.path.join('chat_agent', 'chat_config.json')
        with open(config_path, 'r') as FILE:
            config = json.load(FILE)

        if config['provider'] == 'openai':
            self.chat = ChatOpenAI(config)
        elif config['provider'] == 'palm':
            self.chat = ChatPalm(config)
        elif config['provider'] == 'gpt4all':
            self.chat = ChatGPT4ALL(config)
        else:
            self.chat = ChatDummy(config)

        # context buffer
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
            if '\'action\'' in content or '\"action\"' in content:
                content = content.split(':')[-1]
            links = None

            if action == 'final':
                reply = content
                done = True
                self.context.add(role='assistant', text=content)
            elif action == 'search':
                summary, links = self.search(content)
                text = self.result_template.replace('```summary```', summary)
                text = text.replace('```query```', text)
                self.context.add(role='assistant', text=f'searched for \"{content}\"') 
        self.chat_logger.log_message(f'AI: {reply}') 
        return reply, links
        

class ChatLogging:
    def __init__(self):
        now = datetime.now()
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
        else:
            # vosk and gpt4all don't play in the same sandbox :(
            try:
                from chat_agent.utils.chat_gpt4all import ChatGPT4ALL
            except:
                from utils.chat_gpt4all import ChatGPT4ALL

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
