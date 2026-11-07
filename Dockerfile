FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt anthropic

COPY reviewer ./reviewer
RUN useradd --create-home appuser
USER appuser

EXPOSE 8001
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')"
CMD ["uvicorn", "reviewer.api:app", "--host", "0.0.0.0", "--port", "8001"]
