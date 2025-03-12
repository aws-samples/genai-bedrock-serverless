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
    modelId: str = "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-premier-v1:0" 

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

def retrieve_and_generate(query: str, kb_id: str, model_id: str):
    """Retrieves response from AWS Bedrock with a parameterized model"""
    try:
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={'text': query},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kb_id,
                    'modelArn': model_id  # Use modelId from request
                }
            }
        )
        return response['output']['text']
    except Exception as e:
        print(f"Error in retrieve_and_generate: {e}")
        raise HTTPException(status_code=500, detail=f"AWS Bedrock error: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/query")
async def handle_query(request: QueryRequest):
    """API endpoint to process user queries"""
    try:
        response_text = retrieve_and_generate(request.prompt, request.kbId, request.modelId)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Test changes