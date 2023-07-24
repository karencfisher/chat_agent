import os
import logging
import json
import re
import importlib
import datetime
from threading import Thread
from queue import Queue, Empty

try:
    from chat_agent.memory.context import Context
    from chat_agent.display_code import CodeDisplay
except:
    from memory.context import Context
    from display_code import CodeDisplay


class ChatAgent:
    debug = True

    def __init__(self, verbose=False):
        self.verbose = verbose

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
            object = module.Tool(tool['name'], self.chat, **tool['parameters'])
            self.tools[tool['name']] = {"object": object, "wait": tool['wait']}
            tool_descriptions.append(f'{tool["name"]}: {tool["description"]}')

        # setup sys prompt
        prompt_path = os.path.join('chat_agent', 'sys_prompt.txt')
        with open(prompt_path, 'r') as FILE:
           sys_prompt = FILE.read()

        # get user profile
        profile_path = os.path.join('chat_agent', 'user_profile.txt')
        with open(profile_path, 'r') as FILE:
            user_profile = FILE.read()

        sys_prompt = sys_prompt.format(
                today=datetime.date.today(),
                user_profile=user_profile,
                tool_description='\n'.join(tool_descriptions),
                tool_names=', '.join(list(self.tools.keys())))
        
        # context buffer
        self.context = Context(sys_prompt, 
                               num_response_tokens=config['max_tokens'],
                               max_context_tokens=config['max_context'])

    def __call__(self, text, message_queue):
        # log user input
        self.logger.info(f'User\'s message: {text}')
        self.chat_logger.log_message(f'Human: {text}')

        # setup queue to receive response from tool
        tool_queue = Queue()

        # loop to perform actions scheduled by the LLM
        done = False
        while not done:
            # get complete user prompt
            self.context.add(role='user', text=text)
            prompt = self.context.get_prompt()

            # prompt the LLM
            output = self.chat(prompt)
            self.logger.info(f'AI: {output}')
            self.context.add(role='assistant', text=output)

            # parse response from the LLM
            tool, tool_input, thought = self.__parse(output)
            if thought is not None:
                self.chat_logger.log_message(f'AI: {thought}')
                message_queue.put((False, thought, None))

            # if action is "Final Answer" we are done. Otherwise validate response
            if tool == 'Final Answer':
                done = True
                metadata = None
                continue
            if tool not in list(self.tools.keys()):
                raise KeyError('Invalid tool name')
            
            # if wait is 0, run directly and block for response. Otherwise, run
            # in new thread so we can track it's progress
            if self.tools[tool]['wait'] > 0:
                response = self.__wait_for_tool(tool, tool_input, message_queue)
            else:
                response = self.tools[tool]['object'](tool_input, None)
                if response is None:
                    # we're in trouble
                    raise TimeoutError(f'The {tool} tool did not respond')

            result, metadata = response
            text = f'{text}\n\nObservation: {result}'
                        
        # log final result and push to calling thread
        self.chat_logger.log_message(f'AI: {tool_input}')
        message_queue.put((True, tool_input, metadata))

    def __wait_for_tool(self, tool, tool_input, message_queue, max_iter=10):
        # setup queue to receive response from tool
        tool_queue = Queue()

        # call tool in a new thread so we can monitor its status
        tool_done = False
        tool_thread = Thread(target=self.tools[tool]['object'], 
                             args=(tool_input, tool_queue))
        tool_thread.start()
        message_queue.put((False, "Working...", None))

        iter = 1
        while not tool_done:
            # wait for response from tool. If iteration times out, send
            # message to apprise user it is still in process 
            try:
                response = tool_queue.get(block=True, timeout=self.tools[tool]['wait'])
            except Empty:
                message_queue.put((False, "Working...", None))
                if iter == max_iter:
                    message_queue.put((False, "Tool timedout", None))
                    return None
                iter += 1
            else:
                tool_done = True
        tool_thread.join()
        return response

    def __parse(self, generated: str):
        # check for thoughts to record
        regex = r"Thought: [\[]?(.*?)[\]]?[\n]"
        match = re.search(regex, generated, re.DOTALL)
        if match:
            thought_output = f'{match.group(0)}'
        else:
            thought_output = None

        # is final answer?
        if 'Final Answer:' in generated:
            # filter for code examples (delimited by ```). If so, display code in pop-up
            # window and replace it with "<displayed>" in user response
            pattern = r"```(.*?)```"
            match = re.search(pattern, generated, re.DOTALL)
            if match is not None:
                inner_text = match.group(0)  
                display = CodeDisplay()
                display(inner_text)
                generated = generated.replace(inner_text, '<Displayed>').strip()
            return "Final Answer", generated.split('Final Answer:')[-1].strip(), thought_output

        # find action
        regex = r"Action: [\[]?(.*?)[\]]?[\n]*Action Input:[\s]*(.*)"
        match = re.search(regex, generated, re.DOTALL)
        if not match:
            tool = 'Final Answer'
            tool_input = generated
        else:
            tool = match.group(1).strip()
            tool_input = match.group(2)

        return tool, tool_input.strip(" ").strip('"'), thought_output
        

class ChatLogging:
    def __init__(self):
        now = datetime.datetime.now()
        chat_file = f'chat-{now.strftime("%m.%d.%Y-%H.%M.%S")}.log'
        self.chat_path = os.path.join('chat_agent', 'chats', chat_file)

    def log_message(self, message):
        with open(self.chat_path, 'a') as FILE:
            FILE.write(f'{message}\n\n')        
