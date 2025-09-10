from __future__ import annotations

import json
import smtplib
import ssl
import email.utils
from email.message import EmailMessage
from email.mime.image import MIMEImage
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Optional

from app.config import EMAIL_CONFIG, APP_ROOT


# Paths
QUEUE_PATH: Path = APP_ROOT / EMAIL_CONFIG.get("queue_path", "app/queue/email_queue.json")
TEMPLATE_PATH: Path = APP_ROOT / EMAIL_CONFIG.get("template_path", "app/templates/email_template.html")


def load_template() -> Template:
    return Template(TEMPLATE_PATH.read_text(encoding="utf-8"))


def send_email(to_email: str, image_path: Path | str, retrying: bool = False) -> bool:
    image_path = Path(image_path)

    msg = EmailMessage()
    msg["From"] = f"{EMAIL_CONFIG['from_name']} <{EMAIL_CONFIG['from_email']}>"
    msg["To"] = to_email
    msg["Subject"] = EMAIL_CONFIG["subject"]
    msg["Message-ID"] = email.utils.make_msgid()
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Reply-To"] = EMAIL_CONFIG["from_email"]

    # HTML body with CID reference
    template = load_template()
    body = template.substitute({"image_url": "cid:photo1"})
    msg.set_content("Your photo is attached!")
    msg.add_alternative(body, subtype="html")

    try:
        img_data = image_path.read_bytes()
        # Inline image (CID)
        img_part = MIMEImage(img_data, _subtype="jpeg")
        img_part.add_header("Content-ID", "<photo1>")
        img_part.add_header("Content-Disposition", "inline", filename=image_path.name)
        # Attach inline to the HTML part (payload[1] is the text/html alternative)
        msg.get_payload()[1].add_related(img_data, "image", "jpeg", cid="photo1")
        # If you also want it as an attachment for download, uncomment:
        # msg.attach(img_part)

        smtp_server = EMAIL_CONFIG["smtp_server"]
        smtp_port = EMAIL_CONFIG.get("smtp_port", 25)
        use_tls = EMAIL_CONFIG.get("use_tls", False)
        use_ssl = EMAIL_CONFIG.get("use_ssl", False)

        if use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(EMAIL_CONFIG["username"], EMAIL_CONFIG["password"])
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if use_tls:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                server.login(EMAIL_CONFIG["username"], EMAIL_CONFIG["password"])
                server.send_message(msg)

        print(f"✅ Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"⚠️ Email failed: {e}")
        if not retrying:
            queue_email(to_email, image_path)
        return False


def queue_email(to_email: str, image_path: Path | str) -> None:
    image_path = Path(image_path)
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)

    queue: list[dict] = []
    if QUEUE_PATH.exists():
        queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    queue.append(
        {
            "to": to_email,
            "image": image_path.as_posix(),  # safe, cross-platform JSON string
            "timestamp": datetime.now().isoformat(),
        }
    )

    QUEUE_PATH.write_text(json.dumps(queue, indent=2), encoding="utf-8")
    print("📥 Email added to queue")


def retry_queued_emails() -> None:
    if not QUEUE_PATH.exists():
        return

    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    remaining: list[dict] = []
    for item in queue:
        success = send_email(item["to"], Path(item["image"]), retrying=True)
        if not success:
            remaining.append(item)

    QUEUE_PATH.write_text(json.dumps(remaining, indent=2), encoding="utf-8")
    print(f"🔁 Retried emails. {len(remaining)} remaining.")
