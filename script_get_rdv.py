import sys
import time
import smtplib
import datetime
from email.MIMEText import MIMEText
from getpass import getpass

import requests
from dateutil import parser
from BeautifulSoup import BeautifulSoup


############# CONSTANT & GLOBALS ##################################
# scraping
URL = "https://rdvweb.pointvision.fr//indexNP.aspx?groupemid=65&metier=Opthalmologue&modeMediSite=1&date=&heure=&source="
EVERY = 1  # Minutes before scraping again
MAX_DAYS = 30  # Max gap between today and the rdv.

# e-mailing settings
server = None
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

SENDER = "mandarine.manatea", "Alert Oftalmo"  # Login, Email-Name
TO = "arturo.mondragon@xrce.xerox.com"


def _now():
    return datetime.datetime.now()


############# SCRAPING ##########################################
def get_page_text(url):
    page = requests.get(url, verify=False)

    return page.text


def extract_dates(page_text):
    soup = BeautifulSoup(page_text)

    dates_str = []
    for rdv_str in soup.findAll("input", "pastilleRdv"):
        raw_rdv = rdv_str.attrMap["onclick"]
        date_str = raw_rdv[
            raw_rdv.index("DateRDV") + 17: raw_rdv.index("DateRDV") + 33]
        dates_str.append(date_str)

    return dates_str


def get_min_date(raw_dates):
    now = datetime.datetime.now()

    dates = [
        parser.parse(d, dayfirst=True)
        for d in raw_dates
    ]
    min_date = min(dates)
    print "%s [INFO]: Number of dates found %d" % (str(_now()), len(dates))

    return min_date, (min_date - now).days


############# EMAIL ALERT ##########################################
def set_smtp_server(sender=SENDER,
                    host=SMTP_SERVER, port=SMTP_PORT, timeout=5):
    global server
    login, _ = sender
    server = smtplib.SMTP(host, port, timeout=timeout)
    server.ehlo()
    server.starttls()
    server.login(login, getpass())


def send_alert_mail(sender, to, date, days):
    global server

    MSG_TPL = "Le prochain rdv est le %s dans %d jours."

    msg = MIMEText(MSG_TPL % (str(date), days))

    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = "Un rdv bientot!"

    response = server.sendmail(sender, to, msg.as_string())
    unsent = response.keys()

    if unsent:
        print "%s [WARNING]: Unable to send mail to %s" % (
            str(_now()), str(unsent))

    return unsent


################# WORKERS ################################
def rdv_alert(url=URL, every=EVERY, max_days=MAX_DAYS,
              sender=SENDER, to=TO):
    print "%s [INFO]: Scraping dates" % str(_now())

    date, days = get_min_date(extract_dates(get_page_text(url)))
    _, sender_name = sender
    if days < max_days:
        print "%s [INFO]: Sending mail to" % (str(_now()), to)

        send_alert_mail(sender_name, to, date, days)
    else:
        print "%s [INFO]: No date in range, best date found %s" % (
            str(_now()), str(date))
        sys.stdout.flush()
        time.sleep(every*60)


def alert_worker(*args, **kwargs):
    while True:
        try:
            rdv_alert(*args, **kwargs)
        except Exception as e:
            print "%s [ERROR]", e.message

if __name__ == '__main__':
    set_smtp_server()
    alert_worker()