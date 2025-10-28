FROM python:3.13.7

WORKDIR /app
COPY pyproject.toml pdm.lock* /app/

RUN pip install pdm
RUN pip install --force-reinstall -v "hishel==0.1.5"

RUN pdm install  --prod

COPY . /app/

CMD ["pdm", "run", "start"]