import json
from langchain.schema.output_parser import StrOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from dotenv import load_dotenv

from assistant.prompts import SUMMARY_PROMPT, SEARCH_PROMPT, RESEARCH_PROMPT
from assistant.search import web_search, scrap_text, collapse_list_of_lists

load_dotenv()

search_question_chain = SEARCH_PROMPT | ChatOpenAI(temperature=0) | StrOutputParser() | json.loads

scrape_and_summarize_chain = RunnablePassthrough.assign(
    summary = RunnablePassthrough.assign(
    text=lambda x: scrap_text(x["url"])[:10000]
) | SUMMARY_PROMPT | ChatOpenAI(model="gpt-3.5-turbo-1106") | StrOutputParser()
) | (lambda x: f"URL: {x['url']}\n\nSUMMARY: {x['summary']}")

web_search_chain = RunnablePassthrough.assign(
    urls = lambda x: web_search(x["question"])
) | (lambda x: [{"question": x["question"], "url": u} for u in x["urls"]]) | scrape_and_summarize_chain.map()


full_research_chain = search_question_chain | (lambda x: [{"question": q} for q in x]) | web_search_chain.map()

chain = RunnablePassthrough.assign(
    research_summary= full_research_chain | collapse_list_of_lists
) | RESEARCH_PROMPT | ChatOpenAI(model="gpt-3.5-turbo-1106") | StrOutputParser()
