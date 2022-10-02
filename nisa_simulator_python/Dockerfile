FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
RUN pip install --upgrade pip
COPY ./app /app
RUN pip install --no-cache-dir -r  requirements.txt

EXPOSE 8080

CMD [ "uvicorn", "app.main:app", "--reload","--host", "0.0.0.0", "--port", "8080"]

