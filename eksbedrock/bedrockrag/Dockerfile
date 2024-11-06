FROM python:3.12-slim 

RUN pip3 install -r requirements.txt

ADD bedrockrag.py bedrockrag.py

EXPOSE 8080

ENTRYPOINT [“python3”, “bedrockrag.py”]


