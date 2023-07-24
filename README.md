# chat_agent

## About

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

For code written for us by the AI, it is separated out and displayed it in a popup window. From there one can copy the code to paste into their IDE, for example, to test, add too, etc.

The agent is designed to allow various external tools to be built, following some basic guidelines, and more or less
simply plugged in by registering them in a JSON configuration file. On start up, the agent uses that configuration file
to initialize each tool and make them available in the system prompt to the LLM (currently it works best with OpenAI's
GPT-4, though I am investigating using other open source LLMs, ideally free).

This repository also includes a rudimentary chatbot that uses the chat agent, to allow demonstration and testing. It allows both text (via STDIO) as well as voice interface.

## Want to play with it?

This is a development project, so the best thing would do is to download or clone this repository. E.g.,

```
1) git clone https://github.com/karencfisher/chat_agent.git

2) cd chat_agent

2) create a virtual environment, and activate it (Conda, venv, etc.)

3) pip install -f requirements.txt
```

You will need to make a .env file to contain your API keys. Here is a template:

```
OPENAI_API_KEY = <your openai API key>
GOOGLE_API_KEY = <your Google API key>
GOOGLE_CSE_ID = <your Google custom search enine>
PALM_API_KEY = <your Google PaLM API key>
```

For how to setup Google Programmable Search Engine, get API key, CSE, etc, click [here](https://developers.google.com/custom-search/v1/overview)

To setup OpenAI API use, and get an API key [start here](https://platform.openai.com/)

For Google PaLM 2 API, [start here](https://developers.generativeai.google/) (Has not worked yet with the chat agent, however.)

With all that done, you should be good to go. To run the chat_bot, at the project root, run

```
python chat_bot.py
```

If you want to talk instead of typing, instead run

```
python chat_bot.py voice
```

### Configuration, and costs

The default configuration (chat_agent/chat_config.json) is set up forOpenAI, and the GPT-4 model, as it handles instructions  best. However, it is pricier (i.e., $0.03/thousand input tokens, and $0.06/thousand output tokens). As the context (input to the model) grows as you chat (up to 8k tokens), it can add up. A single user prompt and model response, after a while, might cost around $0.30, for example. If using tools, including search, the cost can be more, as behind the scenes the agent will also call the LLM for intermittent steps, including having it summarize search results. As much as $1.20 or so.

OpenAI's chat-3.5.turbo model is cheaper ($0.0015/thousend input tokens, $0.002/thousand output.) However, it is less instructable -- it might, for example, not heed the system prompt and thus not even use the search tool. Instead, it will just hallucinate.

I am working on working with open source/free LLMs, but so far none follow instructions as well as GPT-4 does.

Also, in any case, currently I am using OpenAI's embedding model (Ada v2) to embed documents as part of the Google search tool. Those cost $0.0001/thousand tokens. (You will need an OpanAI API key, even if you are experimenting with other LLMs. I plan to migrate this to an open source/free sentence embedding model in the future).

## Inspirations

I am inspired by
frameworks such as [LangChain](https://python.langchain.com/docs/get_started/introduction.html)
and Marc Päpper's (much simpler) [LLM-agents](https://github.com/mpaepper/llm_agents).
My approach is somewhere between the two, as it is more specific than an extensive framework such as LangChain,
but more complete than LLM-agents. It is also indirectly inspired by 
[BabyAGI](https://github.com/yoheinakajima/babyagi), though at present I am taking 
different approach in that the steps for a task are determined step by step, a posteriori as it were.


