import json
import boto3
import requests
import logging
import os


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def invoke_aws_rag_agent(prompt):
  
    url = "https://usw1-cai.dmp-us.informaticacloud.com:443/active-bpel/public/rt/37gfTBWcbO7fgYmIsNrMkl/AWSRAGAgent"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, params={"prompt": prompt}, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()  # Assuming the response is in JSON format
        return data.get("enterprise_information", {}).get("UberPlannerPO", {}).get("Planner", {}).get("executor_response", "No executor response found")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching agent response: {e}")
        return {"error": "Failed to fetch agent response"}
    

def lambda_handler(event, context):
 
    
    prompt = ''
   
    api_path = event['apiPath']
    logger.info('API Path')
    logger.info(api_path)
    
    if api_path == '/AWSRAGAgent':
        parameters = event['parameters']
        print ("parameters are: ", parameters)
        
        for parameter in parameters:
            if parameter["name"] == "prompt":
                prompt = parameter["value"]
                
    #    logger.info(timestamp)
    #    logger.info(httperrorcode)
    #    timestamp =  event['parameters']['timestamp']
    #    httperrorcode = event['parameters']['httperrorcode']
        logger.info(prompt)
   
        body = invoke_aws_rag_agent(prompt)
    else:
        body = {"{} is not a valid api, try another one.".format(api_path)}
    
    #print("response_body is: ", response_body )
    response_body = {
        'application/json': {
            'body': json.dumps(body)
        }
    }
        
    print("response_body is: ", response_body )    
    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': 200,
        'responseBody': response_body
    }

    api_response = {
        'messageVersion': '1.0', 
        'response': action_response}
        
    return api_response
    