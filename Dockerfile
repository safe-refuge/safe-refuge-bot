FROM python:3.10.5-alpine3.16
RUN mkdir /app 
COPY main.py /app
COPY pyproject.toml /app 
WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev


ENTRYPOINT [ "poetry run python main.py" ] 