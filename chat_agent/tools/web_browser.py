from webbrowser import open as open_page
try:
    from chat_agent.tools.base_tool import BaseTool
except:
    from tools.base_tool import BaseTool


class Tool(BaseTool):
    def __init__(self, tool_name, llm, **kwargs):
        super(Tool, self).__init__(tool_name, self, llm)
        self.target = kwargs.get('target', 0)

    def run(self, link):
        open_page(link, new=self.target)
        return 'link opened', None
    