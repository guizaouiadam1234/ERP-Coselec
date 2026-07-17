FROM python:3.14-slim

# Set environment variables to ensure python output is straight to terminal (unbuffered)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Environment Variables (Hardcoded to bypass manual Render dashboard entry)
ENV SECRET_KEY="super-secret-key-12345"
ENV MAIL_SERVER="smtp.ethereal.email"
ENV MAIL_PORT="587"
ENV MAIL_USERNAME="louie.pfeffer53@ethereal.email"
ENV MAIL_PASSWORD="dPxQRM9bSS6JB35kUG"
ENV MAIL_FROM="erp@coselec.sn"

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
