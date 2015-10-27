import requests
from BeautifulSoup import BeautifulSoup
from dateutil import parser
import datetime
import smtplib
from getpass import getpass
import time

def get_page_text(url): 

    page = requests.get(url, verify=False)
    return page.text

def get_dates(page_text):

    soup = BeautifulSoup(page_text)
    date_str_list = []
    for rdv_str in soup.findAll("input", "pastilleRdv"):
        raw_rdv = rdv_str.attrMap["onclick"]
        date_str = raw_rdv[raw_rdv.index("DateRDV")+ 17: raw_rdv.index("DateRDV")+ 33]
        date_str_list.append(date_str)
    return date_str_list

def find_gap_min(date_str_list):

    now = datetime.datetime.now()
    # rdv = map(lambda d: parser.parse(d, dayfirst=True), date_str_list)
    rdv = [parser.parse(d, dayfirst=True) for d in date_str_list]
    rdv.sort()
    return (rdv[0] - now).days

def send_gap(gap, mailto, server):

    msg = "\r\n".join([
    	"Subject: Info ophtalmo",
        " ".join(("Le prochain rdv est dans", str(gap), "jours.")),
    ])
    
    server.sendmail(
    "info_ophtalmo@gmail.com", 
    mailto, 
    msg
	)

# -----------------------------------
server = smtplib.SMTP('smtp.gmail.com', 587, timeout=5)
server.ehlo()
server.starttls()
server.login("mandarine.manatea", getpass())

alert = 0

while alert == 0:
    
    url="https://rdvweb.pointvision.fr//indexNP.aspx?groupemid=65&metier=Opthalmologue&modeMediSite=1&date=&heure=&source="
    page_text = get_page_text(url)
    dates = get_dates(page_text)
    gap_min = find_gap_min(dates)

    if gap_min < 30:
        send_gap(gap_min, ["clementine.benoit@gmail.com"], server)
        alert = 1
    else:
        send_gap(gap_min, ["clementine.benoit@gmail.com"], server)
        time.sleep(60*10)
