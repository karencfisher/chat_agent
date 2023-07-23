from easygui import codebox
from threading import Thread
try:
    from chat_agent.tools.base_tool import BaseTool
except:
    from tools.base_tool import BaseTool


class Tool(BaseTool):
    def __init__(self, tool_name, llm, **kwargs):
        super(Tool, self).__init__(tool_name, self, llm)

    def run(self, code):
        display_thread = Thread(target=self.__display, args=(code,))
        display_thread.start()
        return 'code opened', None
    
    def __display(self, code):
        codebox(code)
    