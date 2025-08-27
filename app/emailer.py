import smtplib
import ssl
import json
import os
import email.utils
from email.message import EmailMessage
from email.mime.image import MIMEImage
from datetime import datetime
from app.config import EMAIL_CONFIG, APP_ROOT
from string import Template

QUEUE_PATH = os.path.join(APP_ROOT, EMAIL_CONFIG.get("queue_path", "app/queue/email_queue.json"))
TEMPLATE_PATH = os.path.join(APP_ROOT, EMAIL_CONFIG.get("template_path", "app/templates/email_template.html"))

def load_template():
    with open(TEMPLATE_PATH, "r") as f:
        return Template(f.read())

def send_email(to_email, image_path, retrying=False):
    msg = EmailMessage()
    msg["From"] = f"{EMAIL_CONFIG['from_name']} <{EMAIL_CONFIG['from_email']}>"
    msg["To"] = to_email
    msg["Subject"] = EMAIL_CONFIG["subject"]
    msg["Message-ID"] = email.utils.make_msgid()
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Reply-To"] = EMAIL_CONFIG["from_email"]

    # Prepare HTML body using CID reference
    template = load_template()
    body = template.substitute({"image_url": "cid:photo1"})
    msg.set_content("Your photo is attached!")
    msg.add_alternative(body, subtype="html")

    try:
        with open(image_path, "rb") as img:
            img_data = img.read()
            # Inline image attachment
            img_part = MIMEImage(img_data, _subtype="jpeg")
            img_part.add_header("Content-ID", "<photo1>")
            img_part.add_header("Content-Disposition", "inline", filename=os.path.basename(image_path))
            msg.get_payload()[1].add_related(img_data, "image", "jpeg", cid="photo1")  # attach inline
            # msg.attach(img_part)  # attach also for download

        smtp_server = EMAIL_CONFIG["smtp_server"]
        smtp_port = EMAIL_CONFIG.get("smtp_port", 25)
        use_tls = EMAIL_CONFIG.get("use_tls", False)

        if use_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)
                server.login(EMAIL_CONFIG["username"], EMAIL_CONFIG["password"])
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.login(EMAIL_CONFIG["username"], EMAIL_CONFIG["password"])
                server.send_message(msg)

        print(f"✅ Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"⚠️ Email failed: {e}")
        if not retrying:
            queue_email(to_email, image_path)
        return False

def queue_email(to_email, image_path):
    os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
    queue = []

    if os.path.exists(QUEUE_PATH):
        with open(QUEUE_PATH, "r") as f:
            queue = json.load(f)

    queue.append({
        "to": to_email,
        "image": image_path,
        "timestamp": datetime.now().isoformat()
    })

    with open(QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2)
    print("📥 Email added to queue")

def retry_queued_emails():
    if not os.path.exists(QUEUE_PATH):
        return

    with open(QUEUE_PATH, "r") as f:
        queue = json.load(f)

    remaining = []
    for email in queue:
        success = send_email(email["to"], email["image"], retrying=True)
        if not success:
            remaining.append(email)

    with open(QUEUE_PATH, "w") as f:
        json.dump(remaining, f, indent=2)
    print(f"🔁 Retried emails. {len(remaining)} remaining.")