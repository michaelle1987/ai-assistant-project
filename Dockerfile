FROM python:3.11-slim

WORKDIR /app

# ЯВНО указываем Python где искать модули
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "ai_api/assistant/test_assistant.py"]