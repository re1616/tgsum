FROM python:3.11-slim
WORKDIR /app
COPY bot/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY bot/main.py /app/main.py
CMD ["python","/app/main.py"]
