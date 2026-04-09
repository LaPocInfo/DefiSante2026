FROM python:3.12-slim

RUN apt-get update && apt-get install -y dos2unix && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY run.py .
COPY api/ ./api/
COPY frontend/ ./frontend/

RUN find /app -type f -name "*.py" | xargs dos2unix

EXPOSE 5000

CMD ["python", "run.py"]
