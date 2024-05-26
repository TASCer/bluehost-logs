# https://www.justintodata.com/send-email-using-python-tutorial/
import datetime as dt
import logging
import my_secrets
import smtplib, ssl

from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logging import Logger
from ssl import Purpose

now: datetime = dt.datetime.now()
todays_date: str = now.strftime('%D').replace('/', '-')

email_reciever: list[str] = my_secrets.email_to

email_sender: str = my_secrets.postfix_mail_from
mail_server = my_secrets.postfix_mailhost
email_user = my_secrets.postfix_user
email_password = my_secrets.postfix_password


def send_mail(subject: str, attachment_path: object = None):
    """ Takes a subject (str) and optional file attachment
        Sends email to receiver_email contacts
    """
    logger: Logger = logging.getLogger(__name__)

    msg: MIMEMultipart = MIMEMultipart("alternative")
    msg["Subject"]: str = f"{subject}"
    msg["From"]: str = email_sender
    msg["To"]: str = email_reciever[0]

    if attachment_path:
        html_attachments: str = """\
          <html>
            <body>
              <p><b>Python BLUEHOST Weblogs Report Mailer</b></p>
              <br>
              <p>Please find the xxxxxx report attached.</p>
              <br>
              <p>Visit below for more information</p>
              <a href="https://tascs.test">TASCS - HOA</a>       
            </body>
          </html>
          """
        with open(attachment_path, "rb") as attachment:
            html: MIMEText = MIMEText(html_attachments, "html")
            part_attachments: MIMEBase = MIMEBase("application", "octet-stream")
            part_attachments.set_payload(attachment.read())
            encoders.encode_base64(part_attachments)
            part_attachments.add_header(
                "Content-Disposition",
                "attachment",
                filename=attachment_path
            )
            msg.attach(part_attachments)
            msg.attach(html)
    else:
        html_basic: str = """\
            <html>
              <body>
                <p><b>Python Bluehost Log Parser Report</b>
                <br>
                   Visit <a href="https://www.tascs.test">TASCS</a> 
                   for more information.
                </p>
              </body>
            </html>
            """
        part_basic: MIMEText = MIMEText(html_basic, "html")
        msg.attach(part_basic)

    # NORMAL PORT 25 METHOD WORKING
    with smtplib.SMTP(mail_server, 25) as server:
        try:
            server.sendmail(email_sender, email_reciever, msg.as_string())
            logger.info("emil sent")
        except smtplib.SMTPException as e:
            logger.exception(f"email not sent {str(e)}")

    # PORT 587 w/auth sasl_method = PLAIN phpmailer has it LOGIN
    # try:
    #     with smtplib.SMTP(mail_server, 587, local_hostname= 'tascslt.tascs.local') as server:
    #         server.ehlo()
    #         server.starttls()
    #         server.login(email_user, email_password)
    #         server.sendmail(email_sender, email_reciever, msg.as_string())
    #         logger.info("email sent")
    #
    # except (smtplib.SMTPException) as e:
    #     logger.exception(f"{str(e)}")



 #################################### SSL MODULE TESTING [SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:997)  1123 on RPI4
    # print(ssl.OPENSSL_VERSION)
    # context = ssl.create_default_context(purpose=Purpose.SERVER_AUTH)
    # context.get_ciphers()
    # context.get_ca_certs()
    # # context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3  # Disable SSLv2 and SSLv3
    #
    # try:
    #     with smtplib.SMTP_SSL(mail_server, 587, local_hostname='tascslt.tascs.local', context=context) as server:
    #         server.ehlo()
    #         server.starttls()
    #         server.login(my_secrets.postfix_user, my_secrets.postfix_password)
    #         server.sendmail(my_secrets.mail_from, email_reciever, msg.as_string())
    #         logger.info("emil sent")
    #
    # except (smtplib.SMTPException) as e:
    #     logger.exception(f"{str(e)}")

 # cert = ssl.get_server_certificate(addr=('tascs.test', 587))#, ssl_version=3, ca_certs=None)
    # print(ciphers)
    # print(len(ciphers))
    # # certs = context.load_default_certs()
    # print(len(certs))
    # for c in certs:
    #     issuer = c.get('issuer')
    #     for i in issuer:
    #         print(i[0])
        # print(issuer[2])
    # context.set_ciphers('ALL')        #("TLS_RSA_WITH_AES_128_CBC_SHA256")     # ("TLS_DHE_RSA_WITH_AES_128_GCM_SHA256")
    # context.hostname_checks_common_name = False
    # context.check_hostname = False
    # context.verify_mode = ssl.CERT_NONE
    # ser_cert = ssl.get_server_certificate((my_secrets.postfix_mailhost, 587))
    # context.load_default_certs()
    # ca = context.get_ca_certs()
    # c = context.get_ciphers()journ
    # ciphers = list({x['name'] for x in c})
    # print(ciphers)
    # print(ca)