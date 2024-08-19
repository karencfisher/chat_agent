from webbrowser import open as open_page
from dotenv import load_dotenv
import os
try:
    from chat_agent.tools.base_tool import BaseTool
except:
    from tools.base_tool import BaseTool


class Tool(BaseTool):
    def __init__(self, tool_name, llm, **kwargs):
        super(Tool, self).__init__(tool_name, self, llm)
        self.target = kwargs.get('target', 0)
        load_dotenv()
        self.web = os.getenv('IS_WEBAPP', 'false')

    def run(self, link):
        if not self.web:
            open_page(link, new=self.target)
            return 'link opened', None
        return 'web app', link