import tiktoken
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# Utilities

from youtube_transcript_api import YouTubeTranscriptApi
import os
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from operator import itemgetter

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import TokenTextSplitter
from langchain.text_splitter import HTMLHeaderTextSplitter
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser

from langchain.schema.runnable import RunnablePassthrough, RunnableLambda

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

#New Libraries to be imported
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import Chroma


