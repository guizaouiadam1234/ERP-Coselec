from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from pathlib import Path
from dotenv import load_dotenv


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=(
        os.getenv("MAIL_FROM")
        or os.getenv("MAIL_USERNAME")
        or "no-reply@example.com"
    ),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "localhost"),
    MAIL_STARTTLS=_as_bool(os.getenv("MAIL_STARTTLS"), True),
    MAIL_SSL_TLS=_as_bool(os.getenv("MAIL_SSL_TLS"), False),
    USE_CREDENTIALS=bool(os.getenv("MAIL_USERNAME") and os.getenv("MAIL_PASSWORD")),
    SUPPRESS_SEND=_as_bool(os.getenv("MAIL_SUPPRESS_SEND"), False),
)

fm = FastMail(conf)

async def send_ticket_email(
    email_to: str,
    subject: str,
    body: str
):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype="html"
    )
    await fm.send_message(message)

