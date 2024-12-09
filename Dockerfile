FROM python:3.13.1-slim-bookworm
LABEL authors="DuelitDev"

ENV TZ=Asia/Seoul

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get upgrade -y && apt-get install -y gcc python3-dev && \
    pip install -U pip && pip install --no-cache-dir -r requirements.txt && rm requirements.txt && \
    apt-get remove --purge -y gcc python3-dev && apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY ./src /src
WORKDIR /src

EXPOSE 63149
ENTRYPOINT ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", \
            "-w", "8", "main:app", "--bind", "0.0.0.0:63149"]
