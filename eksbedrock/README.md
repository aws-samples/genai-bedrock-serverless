

## Build scalable containerized RAG based generative AI applications in AWS using Amazon EKS and Amazon Bedrock

1. Build automated and scalable containerized GenAI applications in AWS on using EKS and Bedrock to provide intelligent RAG workflows
2. Automate ingestion of data from multiple data sources using Bedrock Knowledgebases
3. Provide a highly available API interface that allows for pluggable front ends and event driven invocation of LLMs


AWS serverless services make it straightforward to focus on building generative AI applications by providing automatic scaling, built-in high availability, and a pay-for-use billing model. Event-driven compute with AWS Lambda is a good fit for compute-intensive, on-demand tasks such as document embedding and flexible large language model (LLM) orchestration, and Amazon API Gateway provides an API interface that allows for pluggable frontends and event-driven invocation of the LLMs. Our solution also demonstrates how to build a scalable, automated, API-driven serverless application layer on top of Amazon Bedrock and FSx for ONTAP using API Gateway and Lambda.

The solution implements a RAG Retrieval Lambda function that allows RAG with Amazon Bedrock by enriching the generative AI prompt using Amazon Bedrock APIs with your company-specific data and associated metadata (including ACLs) retrieved from the OpenSearch Serverless index that was populated by the embeddings container component. The RAG Retrieval Lambda function stores conversation history for the user interaction in an Amazon DynamoDB table.

### Prerequisites

1. Ensure you have [model access in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) for both the Anthropic Claude v3 and Titan Text Embedding models available on Amazon Bedrock.
2. Install [AWS CLI](https://aws.amazon.com/cli)
3. Install [Docker](https://docs.docker.com/engine/install/)
4. Install [Kubectl](https://kubernetes.io/docs/tasks/tools/)
5. [Install Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli)

### Deploy the solution
Cloning the repository and using the Terraform template will provision all the components of this solution:

1. Clone the repository for this solution:
```
sudo yum install -y unzip
git clone https://github.com/aws-samples/genai-bedrock-fsxontap.git
cd eksbedrock/terraform
```
2. From the _terraform_ folder, deploy the entire solution using terraform:
```
terraform init
terraform apply -auto-approve
```

### Configure EKS

1. Configure a secret for the ECR registry:
```
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin <your account id>.dkr.ecr.<your account region>.amazonaws.com

docker pull <your account id>.dkr.ecr.us-east-2.amazonaws.com/bedrockragrepo:latest

aws eks update-kubeconfig --region <your region> --name eksbedrock

kubectl create secret docker-registry ecr-secret \
  --docker-server=<your account id>.dkr.ecr.<your account region>.amazonaws.com \
  --docker-username=AWS \
  --docker-password=$(aws ecr get-login-password --region <your account region>)

```
2. Navigate to the _kubernetes/ingress_ folder. 
    1. Ensure that the _AWS_Region_ variable in the bedrockragconfigmap.yaml file points to your AWS region.
    2. Replace the image URI in line 20 of the bedrockragdeployment.yaml file with the image URI of your bedrockrag image from your ECR repository.

3. Provision the Kubernetes deployment, service and ingress:
```
cd ..
kubectl apply -f ingress/
```


### Solution Overview

The solution uses Amazon EKS managed node groups to automate the provisioning and lifecycle management of nodes (Amazon EC2 instances) for the Amazon EKS Kubernetes cluster. Every managed node in the cluster is provisioned as part of an Amazon EC2 Auto Scaling group that’s managed for you by EKS.

The EKS cluster consists of a Kubernetes deployment that runs across 2 Availability Zones for high availability where each node in the deployment hosts multiple replicas of a Bedrock RAG container image pulled from Amazon Elastic Container Registry (ECR). This setup makes sure that resources are used efficiently, scaling up or down based on the demand. 

The RAG Bedrock container uses Bedrock Knowledge Base APIs and a Bedrock hosted Claude 3.5 Sonnet LLM to implement a RAG workflow. The solution provides the end user with a scalable endpoint to access the RAG workflow using a Kubernetes service that is fronted by an Amazon Application Load Balancer provisioned via an EKS ingress controller. 

The RAG Bedrock container orchestrated by EKS enables RAG with Amazon Bedrock by enriching the generative AI prompt received from the ALB endpoint with data retrieved from an OpenSearch Serverless index that is synced via Bedrock Knowledge Bases from your company specific data uploaded to Amazon S3.

Here’s a high-level architecture diagram that illustrates the various components of our solution working together as described in the flow above:

![Solution Architecture](/eksbedrock/images/solution-arch.png)



### Test and Validate

#### Create Knowledgebase and load data 

1. Create an S3 bucket and upload your data into the bucket. In our blog we uploaded these 2 files - into our S3 bucket. 
2. Create an Amazon Bedrock knowledge base. Follow the steps [here](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-create.html) to create a knowledge base. Accept all the defaults including using the **Quick create a new vector store** option in Step 7 that creates an Amazon OpenSearch Serverless vector search collection as your knowledge base. 
    1. In Step 5c, provide the S3 URI of the object containing the files for the data source for the knowledge base
    2. Once the knowledge base gets provisioned, obtain the Knowledge base id (kbId) from the Bedrock agents console.

### Query using the AWS Application Load Balancer 

You can query the model directly using the API front end provided by the AWS Application Load Balancer provisioned by the Kubernetes (EKS) Ingress Controller. Obtain this API by navigating to the ALB console.

1. Here’s the curl request you can use for invoking the ALB API for a query related to a document (Bedrock user guide) we uploaded to our data source. Provide the value of the *kbId* parameter and the *modelId* parameter. 
```
curl -X POST "http://k8s-default-bedrockr-9cf4294101-1183110034.us-east-2.elb.amazonaws.com/query" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "What is a bedrock knowledgebase?", "kbId": "L9R1EJRXNY", "modelId": "anthropic.claude-3-5-sonnet-20240620-v1:0"}'
```
### Clean up

To avoid recurring charges, and to clean up your account after trying the solution outlined in this post, perform the following steps:

1. From the _terraform_ folder, delete the Terraform template for the solution:
```
terraform apply --destroy
```
2. Delete the Amazon Bedrock knowledge base. From the Amazon Bedrock console, select the knowledge base you created in this solution, select Delete and follow the steps to delete the knowledge base
