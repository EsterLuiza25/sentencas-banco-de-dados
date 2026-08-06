
FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

RUN poetry config  virtualenvs.create false

COPY pyproject.toml poetry.Lock* /app/

COPY . /app

CMD ["python", "main.py"]