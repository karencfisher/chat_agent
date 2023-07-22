try:
    from chat_agent.tools.base_tool import BaseTool
except:
    from tools.base_tool import BaseTool


class Tool(BaseTool):
    def __init__(self, tool_name, llm, **kwargs):
        super(Tool, self).__init__(tool_name, self, llm)

    def run(self, number):
        return f'Called {number}', None
