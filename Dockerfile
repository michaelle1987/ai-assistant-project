FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ДИАГНОСТИКА - что вообще есть в /app?
RUN ls -la
RUN find . -name "*.py" -type f

# Проверим что в папке ai_api
RUN ls -la ai_api/
RUN ls -la ai_api/assistant/

CMD ["python", "ai_api/assistant/test_assistant.py"]