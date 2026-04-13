FROM python:3.12-slim
WORKDIR /app
COPY requeriments.txt .
RUN pip install --no-cache-dir -r requeriments.txt
COPY . .
CMD ["python", "main.py"]
