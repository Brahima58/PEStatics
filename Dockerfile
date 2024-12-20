FROM python:3.12-slim


RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt


COPY . /app/


COPY templates /app/templates
COPY static /app/static


CMD ["gunicorn", "-b", "0.0.0.0:5000", "PEStatics:app"]


