#!/usr/bin/env python
#-*- coding: utf-8 -*-

import logging
import logging.config
import threading
import inspect
import traceback
import sys

#logging.config.fileConfig('logger.ini')

__logger = logging.getLogger("fapplicator")
__logger.setLevel(logging.DEBUG)
__formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s","%Y-%m-%d %H:%M:%S")
__handler = logging.StreamHandler()
__handler.setFormatter(__formatter)

__logger.addHandler(__handler)

__tLocal = threading.local();

def info(message,ID=None):
    ID=id(threading.current_thread()) if not ID else ID;
    if message.strip():
        callerstack = inspect.stack()[1];
        fLocals = callerstack[0].f_locals;
        if "self" in fLocals:
            __logger.info("%s::%s(0x%x): %s" % (fLocals["self"].__class__,callerstack[3],ID,message))
            return;
        __logger.info("%s(0x%x): %s" % (callerstack[3],ID,message))

def warn(message,ID=None):
    ID=id(threading.current_thread()) if not ID else ID;
    if message.strip():
        callerstack = inspect.stack()[1];
        fLocals = callerstack[0].f_locals;
        if "self" in fLocals:
            __logger.warn("%s::%s(0x%x): %s" % (fLocals["self"].__class__,callerstack[3],ID,message))
            return;
        __logger.warn("%s(0x%x): %s" % (callerstack[3],ID,message))

def critical(message,ID=None):
    ID=id(threading.current_thread()) if not ID else ID;
    if message.strip():
        callerstack = inspect.stack()[1];
        fLocals = callerstack[0].f_locals;
        if "self" in fLocals:
            __logger.critical("%s::%s(0x%x): %s" % (fLocals["self"].__class__,callerstack[3],ID,message))
            return;
        __logger.critical("%s(0x%x): %s" % (callerstack[3],ID,message))

def error(message,ID=None):
    ID=id(threading.current_thread()) if not ID else ID;
    if message.strip():
        callerstack = inspect.stack()[1];
        fLocals = callerstack[0].f_locals;
        if "self" in fLocals:
            __logger.info("%s::%s(0x%x): %s" % (fLocals["self"].__class__,callerstack[3],ID,message))
            return;
        __logger.error("%s(0x%x): %s" % (callerstack[3],ID,message))

def debug(message,ID=None):
    ID=id(threading.current_thread()) if not ID else ID;
    if message.strip():
        callerstack = inspect.stack()[1];
        fLocals = callerstack[0].f_locals;
        if "self" in fLocals:
            __logger.debug("%s::%s(0x%x): %s" % (fLocals["self"].__class__,callerstack[3],ID,message))
            return;
        __logger.debug("%s(0x%x): %s" % (callerstack[3],ID,message))

def getlasterrortraceback():
    return traceback.format_exc();

def getlasterrormsg():
    print(sys.exc_info())
    exception = sys.exc_info()[1];
    return exception.message if exception else "Message missing !";

def setLastMessage(message):
    __tLocal.message = message;

def getLastMessage():
    try:
        return __tLocal.message;
    except:
        return None;
