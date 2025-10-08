FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONBUFFERED 1

WORKDIR /app

# copies requirements.txt into docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copies code into docker
COPY . .

EXPOSE 8080

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "main:app"]

