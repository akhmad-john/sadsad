FROM python:3.8-slim-buster as builder

WORKDIR ./

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
&& apt-get install -y gcc \
&& pip install --upgrade pip \
&& apt-get clean \
&& rm -rf /var/lib/apt

RUN pip wheel --no-cache-dir --no-deps --wheel-dir ./wheels -r requirements.txt

FROM python:3.8-slim-buster

RUN adduser --system app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/static
WORKDIR $APP_HOME

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && apt-get install -y libpq-dev \
    && apt-get install -y netcat \
    && apt-get autoremove --purge \
    && rm -rf /var/lib/apt

COPY --from=builder ./wheels /wheels
COPY --from=builder ./requirements.txt .

RUN pip install --use-deprecated=legacy-resolver --no-cache /wheels/*

COPY ./container/entrypoint.prod.sh $APP_HOME

COPY . $APP_HOME

RUN chown -R app $APP_HOME

USER app

ENTRYPOINT ["/home/app/web/container/entrypoint.prod.sh"]