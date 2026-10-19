FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
EXPOSE 5000
ENV DATABASE=/data/students.db
VOLUME ["/data"]
CMD ["python", "app.py"]
