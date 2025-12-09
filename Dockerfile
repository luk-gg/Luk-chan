FROM python:3.12.12

WORKDIR /app
COPY pyproject.toml pdm.lock* /app/

RUN pip install pdm

RUN pdm install  --prod

COPY . /app/

CMD ["pdm", "run", "start"]