import json
import boto3
import urllib3
from urllib3 import Timeout, PoolManager
import logging
import os


logger = logging.getLogger()
logger.setLevel(logging.INFO)
idmcurl = os.environ.get('IDMC_URL')  #Name of bucket with data file and OpenAPI file


def invoke_aws_rag_agent_supplier(identifier):
    #url = "https://usw1-cai.dmp-us.informaticacloud.com:443/active-bpel/public/rt/37gfTBWcbO7fgYmIsNrMkl/AWSRAGAgent"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Create HTTP pool manager
    http = urllib3.PoolManager()

    prompt = "provide supplier details for " + identifier
    
    # Create the request payload
    payload = json.dumps({"prompt": prompt})

    try:
        # Make the POST request
        response = http.request(
            "POST",
            idmcurl,
            body=payload,
            headers=headers,
            timeout=Timeout(50)
        )

        # Check if the response status is OK
        if response.status != 200:
            logger.error(f"HTTP error: {response.status}")
            return {"error": f"HTTP error: {response.status}"}
        
        # Decode response data
        data = json.loads(response.data.decode("utf-8"))
        return data.get("enterprise_information", {}).get("UberPlannerPO", {}).get("Planner", {}).get("executor_response", "No executor response found")
    
    except Exception as e:
        logger.error(f"Error fetching agent response: {e}")
        return {"error": "Failed to fetch agent response"}
    

def invoke_aws_rag_agent_product(identifier):
    #url = "https://usw1-cai.dmp-us.informaticacloud.com:443/active-bpel/public/rt/37gfTBWcbO7fgYmIsNrMkl/AWSRAGAgent"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Create HTTP pool manager
    http = urllib3.PoolManager()

    prompt = "provide product details for " + identifier
    
    # Create the request payload
    payload = json.dumps({"prompt": prompt})

    try:
        # Make the POST request
        response = http.request(
            "POST",
            idmcurl,
            body=payload,
            headers=headers,
            timeout=Timeout(50)
        )

        # Check if the response status is OK
        if response.status != 200:
            logger.error(f"HTTP error: {response.status}")
            return {"error": f"HTTP error: {response.status}"}
        
        # Decode response data
        data = json.loads(response.data.decode("utf-8"))
        return data.get("enterprise_information", {}).get("UberPlannerPO", {}).get("Planner", {}).get("executor_response", "No executor response found")
    
    except Exception as e:
        logger.error(f"Error fetching agent response: {e}")
        return {"error": "Failed to fetch agent response"}
    

def lambda_handler(event, context):
 
    
    identifier = ''
   
    api_path = event['apiPath']
    logger.info('API Path')
    logger.info(api_path)
    
    if api_path == '/AWSRAGAgentSupplier':
        parameters = event['parameters']
        print ("parameters are: ", parameters)
        
        for parameter in parameters:
            if parameter["name"] == "identifier":
                identifier = parameter["value"]
                
    #    logger.info(timestamp)
    #    logger.info(httperrorcode)
    #    timestamp =  event['parameters']['timestamp']
    #    httperrorcode = event['parameters']['httperrorcode']
        logger.info(identifier)
   
        body = invoke_aws_rag_agent_supplier(identifier)
    
    elif api_path == '/AWSRAGAgentProduct':
        parameters = event['parameters']
        print ("parameters are: ", parameters)
        
        for parameter in parameters:
            if parameter["name"] == "identifier":
                identifier = parameter["value"]
                
    #    logger.info(timestamp)
    #    logger.info(httperrorcode)
    #    timestamp =  event['parameters']['timestamp']
    #    httperrorcode = event['parameters']['httperrorcode']
        logger.info(identifier)
   
        body = invoke_aws_rag_agent_product(identifier)

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
    