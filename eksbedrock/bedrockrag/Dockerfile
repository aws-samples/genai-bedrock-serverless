FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/* 

COPY ./ ./

RUN pip3 install --no-cache-dir -r requirements.txt && \
    pip3 install --upgrade boto3 botocore

EXPOSE 8080

CMD ["uvicorn", "bedrockrag:app", "--host", "0.0.0.0", "--port", "8080"]

