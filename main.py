from lib.core import simbastor

from properties import ATTRIBS

def log():
    import sys
    from lib.shared import log
    log.flush = sys.stdout.flush
    log.write = log.info
    sys.stdout = log;
log()



instance_list = list();
for i in ATTRIBS:
    instance_list.append(simbastor(**i));
