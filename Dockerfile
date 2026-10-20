# Production image for ClothStore: the FastAPI backend also serves the static frontend.
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYDANTIC_AI_NO_BANNER=1

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py ./
COPY backend ./backend
COPY frontend ./frontend

# Run as an unprivileged user that may only write to the uploads folder.
RUN useradd --create-home --uid 1000 app && mkdir uploads && chown app uploads
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]