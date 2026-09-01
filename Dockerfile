FROM python:3.11-slim

# Create a non-root application user
RUN useradd \
    --create-home \
    --shell /usr/sbin/nologin \
    appuser

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .

RUN pip install \
    --no-cache-dir \
    -r requirements.txt

# Verify critical dependencies during the image build
RUN python -c "import psutil; import prometheus_client; print('Dependencies OK')"

# Copy application
COPY app.py .

# Application ownership
RUN chown -R appuser:appuser /app

# Run as non-root
USER appuser

EXPOSE 8000

CMD ["python", "app.py"]