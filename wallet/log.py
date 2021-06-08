
from datetime import datetime

import os

log = None

def LogInit():

    global log

    if not os.path.exists("db"):
        os.makedirs("db")

    if os.path.exists("db/log.csv"):
        log = open("db/log.csv", "a")

    else:
        log = open("db/log.csv", "a")
        log.write('"Time","Method","User ID (From)","User ID (To)","Address","Amount (DOGE)","Fee (DOGE)"\n')
        log.flush()

def Log(label, amount, *, uid_from="", uid_to="", address="", fee=""):
    
    time = datetime.today().strftime("%d/%m/%Y %H:%M:%S");

    log.write('"{0}","{1}",{2},{3},"{4}",{5},{6}\n'.format(time, label, uid_from, uid_to, address, amount, fee))
    log.flush()
