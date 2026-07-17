# syntax=docker/dockerfile:1.7

FROM python:3.12.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PDM_CHECK_UPDATE=false

WORKDIR /app

# PDM fica em uma camada separada e reproduzível
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install "pdm==2.28.0"

# Copiar primeiro somente os arquivos de dependências preserva o cache
COPY pyproject.toml pdm.lock ./

# --no-self porque o código-fonte ainda não foi copiado
# --frozen-lockfile impede o PDM de alterar ou recalcular o lock
RUN --mount=type=cache,target=/root/.cache/pdm \
    pdm install \
    --prod \
    --frozen-lockfile \
    --no-self

COPY . .

# Evita executar a aplicação como root
RUN useradd \
    --system \
    --uid 10001 \
    --home-dir /app \
    appuser \
    && chown -R appuser:appuser /app

USER appuser

CMD ["pdm", "run", "start"]