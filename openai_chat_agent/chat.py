import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# speech recognition and synthesis
try:
    from openai_chat_agent.voice.vosk_recognizer import SpeechRecognize
    from openai_chat_agent.voice.tts import Text2Speech
    from openai_chat_agent.utils.context import Context
    from openai_chat_agent.utils.google_search import GoogleSearch
    from openai_chat_agent.utils.chat_openai import ChatOpenAI, parse
except:
    from voice.vosk_recognizer import SpeechRecognize
    from voice.tts import Text2Speech
    from utils.context import Context
    from utils.google_search import GoogleSearch
    from utils.chat_openai import ChatOpenAI, parse


class ChatAgent:
    debug = True

    def __init__(self, verbose=False):
        load_dotenv()

        # setup logging
        now = datetime.now()
        logfile = f'chatlog-{now.strftime("%m.%d.%Y-%H.%M.%S")}.log'
        logpath = os.path.join('openai_chat_agent', 'logs', logfile)
        logging.basicConfig(handlers=[logging.FileHandler(logpath, 'w', 'utf-8')], 
                            level=logging.INFO, 
                            format='%(message)s')
        self.logger = logging.getLogger()

        # setup sys prompt
        profile_path = os.path.join('openai_chat_agent', 'sys_prompt.txt')
        with open(profile_path, 'r') as FILE:
           sys_prompt = FILE.read()

        # setup chat model and memory
        self.chat = ChatOpenAI()
        self.context = Context(sys_prompt)
        
        # setup search tool
        self.search=GoogleSearch()

    def __call__(self, text):
        self.logger.info(f'Human: {text}\n')
        done = False
        while not done:
            try:
                result = self.chat(text)
                action = result.get['action']
                content = result.get['content']
                
                links = None
                if action is None or action == 'final':
                    done = True

                else:
                    tool = self.tools.get(action)
                    if tool is None:
                        pass
                    else:
                        results = tool['func'](content)
                        text = results['text']
                 

            except Exception as ERR:
                self.logger.error(f'ERROR {ERR}\n')
                if self.debug:
                    raise ERR
                return ERR, None, None
        
    
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
            err, result = self.chat_agent(text)

            if err is None:
                if self.voice:
                    print('\rtalking...     ', end='')
                    self.tts.speak(result)
                else:
                    print(f'AI: {result}\n')
            else:
                print(f'\rError: {err}')

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
