
import threading
import time
import telegram

from .base import CBase
from .sim_buster_transcriber_pickler import CSimTranscriberPickler
from .controller_telegram import CControllerTelegram

from ..shared.log import getlasterrortraceback

class CForwarderTelegram(CBase):
    classname = "forwardur_telegram";

    def __init__(self, transcriber : CSimTranscriberPickler, registerer : CControllerTelegram, frequency : float = 5):
        self.__tr = transcriber;
        self.__is_active = False;
        self.__t = None;
        self.__freq = frequency;
        self.__regr = registerer;
        self.__is_active = False;

    def __del__(self):
        print("killing forwarder (%s)" % str(self));
        self.stop();

    def start(self) -> bool:
        if self.__is_active:
            self.setLastError("Already running");
            return False;
        self.__is_active = True;
        # start thread
        self.__t = threading.Thread(target=self.__loop);
        self.__t.start();
        return True;

    def stop(self) -> bool:
        if not self.__is_active:
            self.setLastError("Not running");
            return False;
        self.__is_active = False;
        self.__t.join();
        del self.__t;
        self.__t = None;
        return True;

    def __loop(self):
        def loopsubj():
            # todo: unjoin sim message reading and storage reading + forwarding (pls concurrency)
            tr = self.__tr;
            tr.writeThatDown(); #dump sim messages to our local storage
            messages = tr.readUnreadMessages(); #read messages from our local storage
            asd = telegram.Bot(self.__regr.bot_token);
            for i in messages:
                body = "From: %(sender)s\nTime: %(date)s\nMessage:\n%(message)s\n" % i;
                for j in self.__regr.getRegistrants():
                    print("Sending message to %s(%s)\nMessage:\n%s" % (j[1] ,j[0] ,body));
                    asd.sendMessage(j[0] ,body);
                # todo: possibly implement concurrency w/ limit
            time.sleep(self.__freq);  # todo: avoid locking when stopping

        while self.__is_active:
            try:
                loopsubj();
            except:
                print(getlasterrortraceback());
                time.sleep(self.__freq)

