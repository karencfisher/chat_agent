'''
Implementation of a basic chatbot to use the agent. Can use either
text (terminal) or voice.
'''

import sys
import re
from threading import Thread
from queue import Queue

from chat_agent.chatagent import ChatAgent
from chat_agent.display_code import CodeDisplay


class Bot:
    def __init__(self, voice=False, verbose=False):
        if voice:
            # initialize voice functions
            print('Initializing speech...')
            from voice.vosk_recognizer import SpeechRecognize
            from voice.tts import Text2Speech

            self.recog = SpeechRecognize()
            self.tts = Text2Speech()
            print('Done')
        
        self.voice = voice
        self.chat_agent = ChatAgent(verbose=verbose)

        self.message_queue = Queue()

    def loop(self):
        # start loop
        text = 'hello'
        while True:
            message_thread = Thread(target=self.chat_agent, 
                                    args=(text, self.message_queue))
            message_thread.start()
            done = False
            while not done:
                message = self.message_queue.get()
                output = self.__filter_codeblocks(message[1])
                if self.voice:
                    print('\rtalking...     ', end='')
                    self.tts.speak(output)
                else:
                    print(f'AI: {output}\n')
                done = message[0]
            message_thread.join()

            if text.lower() == 'goodbye' or text.lower() == 'good bye':
                break

            if self.voice:
                text = ""
                print('\rlistening...     ', end='')
                while text == "":
                    text = self.recog.speech_to_text()
            else:
                text = input('Human: ')
                
        print('\ndone!')

    def __filter_codeblocks(self, generated):
        # filter for code examples (delimited by ```). If so, display code in pop-up
        # window and replace it with "<displayed>" in user response
        pattern = r"```(.*?)```"
        matches = re.findall(pattern, generated, re.DOTALL)
        if matches:
            for match in matches:
                inner_text = f"```{match}```"
                display = CodeDisplay()
                display(inner_text)
                generated = generated.replace(inner_text, '<Displayed>').strip()
        return generated

def main():
    params = {'novoice': False, 'verbose': False}
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in params.keys():
                params[arg] = True
            else:
                raise ValueError(f'Invalid command line argument "{arg}"')
    bot = Bot(voice=not params['novoice'], 
              verbose=params['verbose'])
    bot.loop()

if __name__ == '__main__':
    main()