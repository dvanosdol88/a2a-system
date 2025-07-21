FROM python:3.12-slim
WORKDIR /app
COPY ai_connector.py requirements-ai.txt ./
RUN pip install --no-cache-dir -r requirements-ai.txt
CMD ["python", "ai_connector.py"]
