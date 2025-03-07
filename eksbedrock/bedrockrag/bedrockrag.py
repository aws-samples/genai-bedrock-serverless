import json
import boto3
import os
import textwrap
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from io import StringIO
import sys

# Initialize FastAPI app
app = FastAPI()


# Boto3 client for AWS Bedrock
bedrock_agent_runtime = boto3.client(service_name="bedrock-agent-runtime", region_name='us-east-1')

class QueryRequest(BaseModel):
    prompt: str
    kbId: str

def print_ww(*args, width: int = 100, **kwargs):
    """Wraps and prints output text"""
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

def retrieve_and_generate(query: str, kb_id: str):
    """Retrieves response from AWS Bedrock"""
    response = bedrock_agent_runtime.retrieve_and_generate(
        input={'text': query},
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': 'PNMTFQRPDF',
                'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-premier-v1:0'
            }
        }
    )
    return response['output']['text']

@app.post("/query")
async def handle_query(request: QueryRequest):
    """API endpoint to process user queries"""
    try:
        response_text = retrieve_and_generate(request.prompt, request.kbId)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Test changes