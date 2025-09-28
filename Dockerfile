FROM python:3.13.7

WORKDIR /app
COPY pyproject.toml pdm.lock* /app/

RUN pip install pdm

RUN pdm install  --prod

COPY . /app/

CMD ["pdm", "run", "start"]