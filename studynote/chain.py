import tiktoken
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

from youtube_transcript_api import YouTubeTranscriptApi
import os
import json
import requests
import html2text
from tqdm import tqdm
from bs4 import BeautifulSoup
from operator import itemgetter
import re
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter

#New Libraries to be imported
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from langchain_core.prompts import ChatPromptTemplate

from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.vectorstores import Chroma

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field


## Definitions of the loaders & chains

def yt_loader(yt_ids): #loads youtube videos into a document loader
    
    yt_docs = []
    
    for id in yt_ids:
        loader = YoutubeLoader.from_youtube_url(f"https://www.youtube.com/watch?v={id}",
        add_video_info=True,
        language=["en", "id"],
        translation="en",
        )
    
        yt_docs.extend(RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=50).split_documents(loader.load()))
    
    return yt_docs

def url_loader(urls): # reads urls from a file and loads them into a document loader
    web_docs = []

    for url in urls:
        loader = WebBaseLoader(url)
        web_doc = loader.load()
        for doc in web_doc:
            doc.page_content = doc.page_content.replace("\n", " ")
            doc.page_content = re.sub(r'[^\x00-\x7F]+',' ', doc.page_content)
        
        web_docs.extend(RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=50).split_documents(web_doc))
    
    return web_docs

def convert_bookmarksfile_to_list(bookmarks_file):
    bookmarks = []
    
    with open(bookmarks_file, 'r') as f:
        for line in f:
            bookmarks.append(line.strip()) 
            
    return bookmarks

def convert_bookmarksstr_to_list(bookmarks_str):
    
    bookmarks = bookmarks_str.split('\n')
        
    return bookmarks

def read_bookmarks(bookmarks):
        
    yt_ids=[b.split('youtube.com')[1].split(')')[0].split('?v=')[-1][:11] for b in bookmarks if 'youtube.com' in b]
    urls = [b.split(')')[0].split('(')[-1] for b in bookmarks if 'youtube.com' not in b and 'medium.com' not in b and 'betterprogramming.pub' not in b]

    return yt_ids, urls

def create_docs(bookmarks):
    docs = []
    yt_ids, urls = read_bookmarks(bookmarks)
    yt_docs = yt_loader(yt_ids)
    web_docs = url_loader(urls)
    
    docs.extend(yt_docs)
    docs.extend(web_docs)
    
    return docs

def create_retrieverdb(docs):
    vectordb = Chroma.from_documents(
                docs,
                embedding=OpenAIEmbeddings(),
                persist_directory='./data'
                )
    vectordb.persist()
    
    retrieverdb = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    
    return vectordb, retrieverdb

def create_llm(model ="gpt-3.5-turbo-1106", temperature = 0.0):
    llm = ChatOpenAI(model=model, temperature= temperature, verbose=True)
    
    return llm

def read_inputs(input_file):
    with open(input_file, 'r') as f:
        text = f.read()
        
    return text

class Output(BaseModel):
    title: str = Field(description="title of the note")
    metadata: list = Field(description="metadata of the note")
    note: str = Field(description="note compiled based on the title and the document")

def create_prompt(system_message, user_message):
        prompt = ChatPromptTemplate.from_messages([
                ("system", system_message),
                ("human", user_message)
                ]
            )
        
        return prompt

#bookmarks = input("Enter the path to your bookmarks file: ")
#title = input("Enter the title of your note: ")

def chain_invoke(title, bookmarks):

    docs = create_docs(bookmarks)

    vectordb, retrieverdb = create_retrieverdb(docs)

    metadata = read_inputs('/home/dpvj/git/assistant/studynote/inputs/metadata.md')
    style = read_inputs('/home/dpvj/git/assistant/studynote/inputs/style.md')
    example = read_inputs('/home/dpvj/git/assistant/studynote/example/Langchain - RAG Techniques.md')

    llm = create_llm()

    system_message = """
            You are a world class note taking assistant.
            You summarize notes into concise manner extracting the most relevant information.
            
            First, you populate the metadata based on the user document and the information below:
            - output the metadata based on the format_instructions provided at the end of this message
            - fill in after the colon :
            - if you don't have a value or specified to do, leave it blank, but keep the fields     
            - the metatdata is contained between the dotted lines immediately preceding this instruction
            
            ----------------------------------------------
            {metadata} 
            ----------------------------------------------
            
            Second, use the information provided in the style to summarize the note folllowing the guidelines below:
            - keep within the information in given in the text, do not make things up - unless you are asked for examples.
            - ensure that the style is the same as provided between the dotted lines immediately preceding this instruction.
            
            ----------------------------------------------
            {style}
            ----------------------------------------------
            
            Thirdly, you are also provided an example note for reference. Your note should follow the same structure as the example note.
            This example contains both the metadata and the style. You are to separate the metadata from the style and use them accordingly.
            
            ----------------------------------------------
            {example}
            ----------------------------------------------
        """

    user_message = """Use the following document to summarize into a note under the specified title
            the note must follow a specified styleand  specified style:
            
            <document>
            {context}
            </document>
            
            title: {input}"""

    prompt = create_prompt(system_message, user_message)

    chain = (
        {
            "context": itemgetter("input") | retrieverdb,
            "input": itemgetter("input"),
            "style": itemgetter("style"),
            "example": itemgetter("example"),
            "metadata": itemgetter("metadata")
        }
        | prompt
        | llm
    )

    response = chain.invoke({"input": title, "style": style, "example": example, "metadata": metadata})

    output_dir = "/home/dpvj/git/assistant/studynote/outputs"
    output_file = os.path.join(output_dir, f"{title}.md")

    with open(output_file, "w") as f:
        f.write(response.content)

    vectordb.delete_collection()
    
    return output_file



#print(f"Note on {response['title']} saved to {output_file}")

#for item, value in response["metadata"][0].items():
#    print(f"{item}: {value}")