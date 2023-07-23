# chat_agent

This is building a conversational AI agent, integrating ideas about autonomous agents and 
[ReAct](https://react-lm.github.io/). The ultimate goal is to have a friendly, empathic, and helpful
virtual assistant that can run in the background as one works. It's primary modality is to use
voice, with the ability to also display useful information on one's screen. For example, if the agent
has performed an online search and summarizes the information it found, it can also provide you
with the relevant URLs it consulted and, on request, open one or more of the links in your local
browser for further perusal. It can even chain these steps together, such as in:

```
AI: Hello Karen! How can I assist you today?

Human: can you find and open for me documentation on the python random library

AI: Thought: Karen is asking for documentation on the Python random library. I will need to search for this online.

AI: Thought: I have found the documentation for the Python random library. I will now open the link for Karen.

[the agent opens the link on Karen's browser]

AI: I have accomplished your task of finding and opening the documentation for the Python random library. You should now be able to see the documentation in your browser. Is there anything else you need help with, Karen?
```

Or, similarly, if it provides you a block of code (to perhaps illustrate a library function or alogorithm), it can 
load the code into a REPL (for example, if Python) which can then be executed, modified, etc. Otherwise, a simple 
popup window from which you can copy the code and paste it into your IDE.

I am inspired by
frameworks such as [LangChain](https://python.langchain.com/docs/get_started/introduction.html)
and Marc Päpper's (much simpler) [LLM-agents](https://github.com/mpaepper/llm_agents).
My approach is somewhere between the two, as it is more specific than an extensive framework such as LangChain,
but more complete than LLM-agents. It is also indirectly inspired by 
[BabyAGI](https://github.com/yoheinakajima/babyagi), though at present I am taking 
different approach in that the steps for a task are determined step by step, a posteriori as it were.


