FROM python:3.14-slim

# Set environment variables to ensure python output is straight to terminal (unbuffered)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Environment Variables (Hardcoded to bypass manual Render dashboard entry)
ENV SECRET_KEY="super-secret-key-12345"
ENV MAIL_SERVER="smtp.resend.com"
ENV MAIL_PORT="465"
ENV MAIL_USERNAME="resend"
# IMPORTANT: Set MAIL_PASSWORD to your Resend API Key in production (Render ENV vars)
ENV MAIL_PASSWORD=""
ENV MAIL_FROM="noreply@coselec.sn"
ENV MAIL_STARTTLS="false"
ENV MAIL_SSL_TLS="true"

WORKDIR /app

# Install dependencies first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
