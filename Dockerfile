FROM python:3.12-slim
ENV PYTHONPATH="${PYTHONPATH}:/app"
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requeriments.txt
COPY . .
CMD ["python", "main.py"]
