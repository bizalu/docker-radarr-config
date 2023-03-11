FROM python:latest
LABEL Maintainer="bizalu"

WORKDIR /app/radarr-config/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY config/ ./

CMD [ "python", "/app/radarr-config/init-config.py"]