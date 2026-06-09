FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend source code
COPY frontend/ /app/frontend/

# Expose default Streamlit port
EXPOSE 8501

# Disable telemetry and host the application
ENV PYTHONUNBUFFERED=1

CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
