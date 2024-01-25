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
email_sender: str = my_secrets.mail_from
email_from: str

mail_server = my_secrets.postfix_mailhost


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
              <p><b>Python HOA Insights Report Mailer</b></p>
              <br>
              <p>Please find the bi-monthly community changes report attached.</p>
              <br>
              <p>Visit below for more information</p>
              <a href="https://hoa.tascs.locaL">TASCS - HOA</a>       
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
                <p><b>Python Report Mailer</b>
                <br>
                   Visit <a href="https://roadspies.tascs.test">ROADSPIES</a> 
                   for more information.
                </p>
              </body>
            </html>
            """
        part_basic: MIMEText = MIMEText(html_basic, "html")
        msg.attach(part_basic)

    # NORMAL PORT 25 METHOD WORKING
    # with smtplib.SMTP(mail_server, 25) as server:
        # try:
        #     server.sendmail(email_sender, email_reciever, msg.as_string())
        #     logger.info("emil sent")
        # except smtplib.SMTPException as e:
        #     logger.exception(f"email not sent {str(e)}")

    # PORT 587 w/auth sasl_method = PLAIN phpmailer has it LOGIN
    # try:
    #     with smtplib.SMTP(mail_server, 587, local_hostname= 'tascslt.tascs.local') as server:
    #         server.starttls()
    #         server.login(my_secrets.postfix_user, my_secrets.postfix_password)
    #         server.ehlo()
    #         # server.starttls()
    #         server.sendmail(my_secrets.mail_from, email_reciever, msg.as_string())
    #         logger.info("emil sent")
    #
    # except (ssl.ALERT_DESCRIPTION_HANDSHAKE_FAILURE, smtplib.SMTPException) as e:
    #     logger.exception(f"{str(e)}")



 #################################### SSL MODULE TESTING
    print(ssl.OPENSSL_VERSION)
    # paths = ssl.get_default_verify_paths(cafile='./misc/tascs.test.pem', capath='./misc/tascs.test.pem')
    # print(paths)
    # context = ssl.create_default_context(purpose=Purpose.SERVER_AUTH, cafile='TESTS-CA.pem', capath='/home/todd//tascs.test.pem')
    context = ssl.create_default_context(purpose=Purpose.SERVER_AUTH, cafile=None, capath=None)
    ciphers = context.get_ciphers()
    print(len(ciphers))
    # certs = context.get_ca_certs()
    # # certs = context.load_default_certs()
    # print(len(certs))
    # for c in certs:
    #     issuer = c.get('issuer')
    #     for i in issuer:
    #         print(i[0])
        # print(issuer[2])
    # context.set_ciphers('TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384')        #("TLS_RSA_WITH_AES_128_CBC_SHA256")     # ("TLS_DHE_RSA_WITH_AES_128_GCM_SHA256")
    # context.hostname_checks_common_name = False
    # context.check_hostname = False
    # context.verify_mode = ssl.CERT_NONE
    # ser_cert = ssl.get_server_certificate((my_secrets.postfix_mailhost, 587))
    # context.load_default_certs()
    ca = context.get_ca_certs()
    # c = context.get_ciphers()journ
    # ciphers = list({x['name'] for x in c})
    # print(ciphers)
    # print(ca)
    try:
        with smtplib.SMTP_SSL(mail_server, 587, local_hostname='tascslt.tascs.local', context=context) as server:
            server.starttls()
            server.login(my_secrets.postfix_user, my_secrets.postfix_password)
            server.ehlo()
            # server.starttls()
            server.sendmail(my_secrets.mail_from, email_reciever, msg.as_string())
            logger.info("emil sent")

    except (smtplib.SMTPException) as e:
        logger.exception(f"{str(e)}")

