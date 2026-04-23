FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    WORKSHOP_BACKEND_HOST=0.0.0.0 \
    PORT=7860

WORKDIR /app

COPY requirements.txt ./requirements.txt
COPY pyproject.toml ./pyproject.toml
RUN pip install --upgrade pip && pip install poetry && poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

COPY backend ./backend
COPY utils ./utils
COPY notebooks ./notebooks
COPY src ./src

EXPOSE 7860
CMD ["./backend/run_huggingface.sh"]
