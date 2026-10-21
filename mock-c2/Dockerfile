FROM python:3.11-slim
RUN pip install flask
WORKDIR /app
COPY app.py /app/app.py
EXPOSE 80
CMD ["python", "/app/app.py"]
