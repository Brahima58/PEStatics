FROM python:3.12-slim


WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev


COPY requirements.txt /app/


RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

COPY templates /app/templates
COPY static /app/static

CMD ["gunicorn", "-b", "0.0.0.0:5000", "PEStatics:app"]



