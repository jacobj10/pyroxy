FROM python:3.7.4

ADD ./ /app
WORKDIR /app

RUN pip3 install -r /app/requirements.txt

ENTRYPOINT ["/bin/sh", "-c", "/app/run_example.sh"]
