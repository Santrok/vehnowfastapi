FROM python

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

WORKDIR /app

COPY . .

