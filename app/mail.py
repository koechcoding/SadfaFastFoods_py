import os
from flask_mail import Mail, Message
from jinja2 import Environment, PackageLoader, select_autoescape

mail = Mail()
env = Environment(
    loader=PackageLoader('app', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


def email_verification_mail(token=None, recipient=None):
    if token is None or recipient is None:
        return
    template = env.get_template('email_verification.html')
    msg = Message(
        'Email Verification',
        sender='andela.book.a.meal@gmail.com',
        recipients=[recipient])
    msg.html = template.render(
        message={'link': os.getenv('EMAIL_VERIFICATION_ENDPOINT') + token})
    mail.send(msg)


def password_reset_mail(token=None, recipient=None):
    if token is None or recipient is None:
        return
    template = env.get_template('password_reset.html')
    msg = Message(
        'Password Reset',
        sender='andela.book.a.meal@gmail.com',
        recipients=[recipient])
    msg.html = template.render(
        message={'link': os.getenv('PASSWORD_RESET_ENDPOINT') + token})
    mail.send(msg)
