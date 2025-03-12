

## Build scalable containerized RAG based generative AI applications in AWS using Amazon EKS and Amazon Bedrock

1. Build automated and scalable containerized GenAI applications in AWS on using EKS and Bedrock to provide intelligent RAG workflows
2. Automate ingestion of data from multiple data sources using Bedrock Knowledgebases
3. Provide a highly available API interface that allows for pluggable front ends and event driven invocation of LLMs


### Prerequisites

1. Install [AWS SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html).
2. Clone the repository for this solution:

```
sudo yum install -y unzip
git clone git@github.com:aws-samples/genai-bedrock-serverless.git 
cd eksbedrock
```
### Install

1. From the _eksbedrock_ folder, deploy the SAM template for the solution:
```
sam build -t template.yaml
sam deploy --resolve-s3 --stack-name <anyname> --capabilities CAPABILITY_NAMED_IAM
```
2. The template creates 2 [Amazon S3](https://aws.amazon.com/s3/) buckets. Navigate to the output section of the deployed SAM template on the [AWS CloudFormation](https://aws.amazon.com/cloudformation/) console to obtain the names of these 2 S3 buckets (ProductDocsBucket and CloudOpsSupportBucket) so that you can locate them on the S3 console.
    - Upload the _ProductErrorCodes.xlx_ file from the _data_ folder in our solution to the ProductDocsBucket bucket in the S3 console.
    - Upload the _cloudopsupport.json_ and the _applogs.csv_ files from the _data_ folder in our solution to the CloudOpsSupportBucket bucket in the S3 console.
3. Create an Amazon Bedrock knowledge base. Follow the steps [here](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-create.html) to create a knowledge base. Accept all the defaults including using the **Quick create a new vector store** option in Step 7 that creates an Amazon OpenSearch Serverless vector search collection as your knowledge base. Configure the following areas specific to our use case in the solution:
    1. In Step 4a provide an optional description for your knowledge base as “_Provides error resolution based on error description of the error_”
    2. In Step 5c where you need to provide the S3 URI of the object containing the files for the data source for the knowledge base, select the S3 URI of the ProductDocsBucket

### Solution Overview

Here’s a high-level architecture diagram that illustrates the various components of our solution working together as described in the flow above:

![Solution Architecture](/eksbedrock/images/solution-arch.png)

### Setup

1. Create an Amazon Bedrock Agent. Follow the steps [here from the Bedrock Agents console](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-create.html) to create your Bedrock agent. Accept all the defaults except in the following areas that are specific to the configuration for our solution. In the **Configure your agent** section:
    1. In Step 2c to **Select a Model**, select the Anthropic Claude 3 Sonnet model. In Step 2d, under **Instructions for the agent**, provide the following instruction “_You are an agent that provides error resolution and affected application component information based on the HTTP error code and timestamp of the error_”
2. In Step 2g in the **IAM permissions** sections for the Agent resource role, select **Use an existing service role** and select the ‘_AmazonBedrockExecutionRoleForAgents_CloudOps’_ IAM service role that has been provisioned for you by the solution’s SAM template.
3. In Step 3 to add an action group to the Bedrock Agent, follow the [steps here to add an action group from the console](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-action-add.html).
    1. In step 6 within the **Action group type** section select **Define with API schemas** as shown below
    2. In step 7 within the **Action group invocation** section select **Select an existing Lambda function** and select the _cloudops-bedrockagent_ Lambda function already provisioned for you.
    3. In step 8 under the **Action group schema section,** select **Select an existing API schema,** select the **Browse S3** button and select the _cloudsopssupport.json_ file from the CloudOpsSupportBucket S3 bucket provisioned in your account.
    4. In Step 4 in the Knowledge bases section, select **Add** to associate your knowledge group that you created in the pre-requisites section with your agent as shown below:


### Test and Validate

The Amazon Bedrock console provides a UI to test your agent. [Follow the steps here to test and prepare your agent](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-test.html) so that is ready to deploy. [Follow the steps here to deploy your agent](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-deploy.html) by creating an alias for the agent and an agent version that is associated to that alias. You are now ready to test your agent. 

Provide a sample prompt in the Bedrock agent UI where as a support analyst you are looking to resolve an error based on an HTTP error code and timestamp of the error provided by the application. You can look for sample error codes and associated timestamps in the sample application log file that we have provided in our solution. Here's a sample prompt and the agent response providing detailed error resolution and citation of sources where it obtained information to resolve the error:

![Sample prompt](/cloudops/images/sample-prompt.png) 

By selecting **Show trace** for the response, a dialog box shows the reasoning technique used by the agent and the final response generated by the FM.

![Agent Trace 1](/cloudops/images/agent-trace1.png)

![Agent Trace 2](/cloudops/images/agent-trace2.png)

![Agent Trace 3](/cloudops/images/agent-trace3.png)


### Clean up

To avoid recurring charges, and to clean up your account after trying the solution outlined in this post, perform the following steps:

1. From the _cloudops_ folder, delete the SAM template for the solution:
```
sam delete --stack-name <yourstackname> --capabilities CAPABILITY_NAMED_IAM
```
2. Delete the Amazon Bedrock Agent. From the Amazon Bedrock console, select the Agent you created in this solution, select Delete and follow the steps to delete the agent
3. Delete the Amazon Bedrock knowledge base. From the Amazon Bedrock console, select the knowledge base you created in this solution, select Delete and follow the steps to delete the knowledge base
