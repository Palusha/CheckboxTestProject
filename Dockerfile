FROM python:3.11.2-alpine

ENV PYTHONDONTWRITEBYTECODE 1  
ENV PYTHONUNBUFFERED 1  

WORKDIR /home/app

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip3 install --upgrade pip

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /home/app/entrypoint.sh
RUN chmod +x /home/app/entrypoint.sh

COPY . .

ENTRYPOINT ["/home/app/entrypoint.sh"]
