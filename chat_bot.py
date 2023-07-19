'''
Implementation of a basic chatbot to use the agent. Can use either
text (terminal) or voice.
'''

import sys
import importlib
from threading import Thread
from queue import Queue

from chat_agent.chatagent import ChatAgent


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
                if self.voice:
                    print('\rtalking...     ', end='')
                    self.tts.speak(message[1])
                else:
                    print(f'AI: {message[1]}\n')
                done = message[0]
            message_thread.join()

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