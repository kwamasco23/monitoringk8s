FROM python:3.11-slim

RUN useradd \
    --create-home \
    --shell /usr/sbin/nologin \
    appuser

WORKDIR /app

COPY requirements.txt .

RUN pip install \
    --no-cache-dir \
    -r requirements.txt

RUN python -c "import psutil; import prometheus_client; print('Dependencies OK')"

COPY app.py .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["python", "app.py"]