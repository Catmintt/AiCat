import aiosmtplib
from email.message import EmailMessage
from .config import settings

async def send_email(to_email: str, subject: str, body: str):
    """异步发送邮件"""
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = settings.EMAIL_USER
    msg['To'] = to_email
    msg.set_content(body)

    try:
        # 使用 aiosmtplib.SMTP 异步发送
        async with aiosmtplib.SMTP(
            hostname=settings.EMAIL_HOST, 
            port=settings.EMAIL_PORT, 
            use_tls=True
        ) as server:
            await server.login(settings.EMAIL_USER, settings.EMAIL_PASS)
            await server.send_message(msg)
        print(f"邮件已成功异步发送至 {to_email}")
    except Exception as e:
        print(f"异步发送邮件失败: {e}")