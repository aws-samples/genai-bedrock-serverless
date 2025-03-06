import json
import boto3
import os
import textwrap

from langchain.chains import ConversationChain
from langchain.llms.bedrock import Bedrock
from langchain.embeddings import BedrockEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


from io import StringIO
import sys
import textwrap

def print_ww(*args, width: int = 100, **kwargs):
    """Like print(), but wraps output to `width` characters (default 100)"""
    buffer = StringIO()
    _stdout = sys.stdout
    try:
        sys.stdout = buffer
        print(*args, **kwargs)
        output = buffer.getvalue()
    finally:
        sys.stdout = _stdout
    for line in output.splitlines():
        print("\n".join(textwrap.wrap(line, width=width)))

 
def retrieveAndGenerate(query, region_name, kbId):
    
    bedrock_agent_runtime = boto3.client(service_name = "bedrock-agent-runtime", region_name=region_name)
    return bedrock_agent_runtime.retrieve_and_generate(
        input={
            'text': query
        },
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': kbId,
                'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-instant-v1:2:100k'
                }
            }
        )
    

def lambda_handler(event, context):
    # INITIALIZE 
    event_body = json.loads(event["body"])
    region_name = os.environ['region']
    query = event_body["prompt"]
    kbId = event_body["kbId"]
    
    response = retrieveAndGenerate(query, region_name,kbId)
    print_ww(response['output']['text'])
  
   
   
   
    
    
    
        
    
    
   

