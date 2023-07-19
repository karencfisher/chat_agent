import logging


class BaseTool:
    def __init__(self, tool_name, tool_object, **kwargs):
        self.__tool_name = tool_name
        self.__tool_object = tool_object
        self.logger = logging.getLogger('chat_log')

    @property 
    def get_name(self):
        return self.tool_name
    
    @property
    def get_object(self):
        return self.tool_object

    def __call__(self, input, tool_queue):
        result = self.run(input)
        tool_queue.put(result)
    
    def run(self, input):
        return (f'Dummy tool, input was {input}', None)
    
    def post_process(self, **args):
        raise NotImplementedError('post_process method not implemented.')
    