import json
import boto3
import sqlite3
from datetime import datetime
import random
import logging
import os
import csv

logger = logging.getLogger()
logger.setLevel(logging.INFO)
cursor = None
conn = None
applogs_db = '/tmp/applogs.db'

s3 = boto3.client('s3')
bucket = os.environ.get('BUCKET_NAME')  #Name of bucket with data file and OpenAPI file
cw_log_file = 'applogs.csv' #Location of data file in S3
local_db = '/tmp/applogs.csv' #Location in Lambda /tmp folder where data file will be copied

#Download data file from S3
s3.download_file(bucket, cw_log_file, local_db)

#Initial data load and SQLite3 cursor creation 
def load_data():
    # create db
    global conn
    conn = sqlite3.connect(applogs_db)
    cursor = conn.cursor()
    logger.info('Completed initial data load ')

    # Creating table 
    table ="""CREATE TABLE AppLogsDB(HTTPErrorCode VARCHAR(255), Timestamp VARCHAR(255), 
    Description VARCHAR(255));"""
    cursor.execute(table) 

# Queries to INSERT records. 
    cursor.execute('''INSERT INTO AppLogsDB VALUES ('500', '202404219:00', 'Sample Description1')''')
    cursor.execute('''INSERT INTO AppLogsDB VALUES ('404', '202404220:00', 'Sample Description2')''') 
    cursor.execute('''INSERT INTO AppLogsDB VALUES ('403', '202404221:00', 'Sample Description3')''') 
   
# Display data inserted 
    print("Data Inserted in the table: ") 
    data=cursor.execute('''SELECT * FROM AppLogsDB''') 
    for row in data: 
	    print(row) 

# Commit your changes in the database	 
    conn.commit() 
    return cursor
    
#Initial data load and SQLite3 cursor creation 
def load_data_s3():
# create db
    global conn
    conn = sqlite3.connect(applogs_db)
    cursor = conn.cursor()
    logger.info('Completed initial data load ')

# Creating table 
    table ="""CREATE TABLE AppLogsDB(HTTPErrorCode VARCHAR(255), Timestamp VARCHAR(255), 
    Description VARCHAR(255));"""
    cursor.execute(table) 
    
# Load data file. 
    with open('/tmp/applogs.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
        # Insert the data into the table
            cursor.execute('''INSERT INTO my_table (HTTPErrorCode, Timestamp, Description) VALUES (?,?,?)''', row)
        
# Display data inserted 
    print("Data Inserted in the table: ") 
    data=cursor.execute('''SELECT * FROM AppLogsDB''') 
    for row in data: 
	    print(row) 

# Commit your changes in the database	 
    conn.commit() 
    return cursor
    
#Function returns error details based on error date/time and high level description
def get_error_description(httperrorcode, timestamp):
  
    cursor.execute("select Description from AppLogsDB where HTTPErrorCode like ? and Timestamp like ?", ("%" + httperrorcode + "%", "%" + timestamp + "%"))
    error_description = cursor.fetchone()[0]
    return error_description
  

def lambda_handler(event, context):
 
    global cursor
    if cursor == None:
        cursor = load_data_s3()
    
    id = ''
    api_path = event['apiPath']
    logger.info('API Path')
    logger.info(api_path)
    
    if api_path == '/get_error_description':
        parameters = event['parameters']
        timestamp =  event['parameters']['timestamp']
        httperrorcode = event['parameters']['httperrorcode']
        body = get_error_description(httperrorcode, timestamp)
    else:
        body = {"{} is not a valid api, try another one.".format(api_path)}

    response_body = {
        'application/json': {
            'body': json.dumps(body)
        }
    }
        
    action_response = {
    #    'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
    #    'httpMethod': event['httpMethod'],
        'httpStatusCode': 200,
        'responseBody': response_body
    }

    api_response = {
        'messageVersion': '1.0', 
        'response': action_response}
        
    return api_response