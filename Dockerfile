FROM python:3.10.5-alpine3.16
RUN mkdir /app 
COPY main.py /app
COPY pyproject.toml /app 
WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
RUN apk add --update py3-pip
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev


ENTRYPOINT [ "poetry run python main.py" ] 