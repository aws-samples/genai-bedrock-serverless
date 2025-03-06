FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/* 

COPY ./ ./

RUN pip3 install -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["python3", "bedrockrag.py"]
