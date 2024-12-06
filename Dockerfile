
FROM python:3.12-slim

WORKDIR /app


COPY requirements.txt /app/


RUN pip install --no-cache-dir -r requirements.txt


COPY . /app/


CMD ["gunicorn", "-b", "0.0.0.0:5000", "PEStatics:app"]


EXPOSE 8080
