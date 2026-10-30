FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MPLBACKEND=Agg \
    TF_CPP_MIN_LOG_LEVEL=2 \
    WORKSHOP_BACKEND_HOST=0.0.0.0 \
    PORT=7860

# Hugging Face Spaces run the container as uid 1000.
RUN useradd -m -u 1000 user

WORKDIR /app

COPY pyproject.toml ./pyproject.toml
RUN pip install --upgrade pip && pip install poetry && poetry config virtualenvs.create false \
    && poetry install --no-root --only main --no-interaction --no-ansi

COPY --chown=user backend ./backend
COPY --chown=user utils ./utils
COPY --chown=user notebooks ./notebooks
COPY --chown=user src ./src
RUN mkdir -p /app/backend/data && chown user /app/backend/data

USER user
EXPOSE 7860
CMD ["./backend/run_huggingface.sh"]
