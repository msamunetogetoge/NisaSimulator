FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
RUN pip install --upgrade pip
COPY ./app /app
RUN pip install --no-cache-dir -r  requirements.txt

ENV PORT 8080
WORKDIR /app

CMD [ "uvicorn", "main:app", "--reload","--host", "0.0.0.0", "--port", "8080"]

