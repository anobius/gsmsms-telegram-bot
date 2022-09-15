import threading
import os

import _pickle as cPickle

from .transcriber_base import CTranscriber
from .sim_buster import CMBuster;


# todo: other storage types
class CSimTranscriberPickler(CTranscriber):
    classname = "sim_buster_transcriber_pickler";

    def __init__(self, cmbuster_instance: CMBuster, storage_file: str = "/tmp/messages.pickol"):
        self.__cmb = cmbuster_instance;
        self.__storage_file = storage_file;
        self.__sema = threading.BoundedSemaphore();
        super().__init__();

    def _initialize_files(self):
        if not os.path.isfile(self.__storage_file) or os.path.getsize(self.__storage_file) == 0:
            print("Storage file uninitialized or broke down to 0 bytes for some reason!");
            f = open(self.__storage_file,"wb+");
            f.write(cPickle.dumps([[],[]]));
            f.close();

    def __updateRecords(self,sms_data: dict) -> bool:
        with self.__sema:
            db = open(self.__storage_file, "ab+");
            db.seek(0);
            # data format: [[list of unread pdu msgs],[list of read msgs]]
            data = cPickle.loads(db.read());
            data[0].append(sms_data);
            db.truncate(0);
            db.write(cPickle.dumps(data));
            db.close();
            return True;

    def writeThatDown(self) -> bool:
        cmb = self.__cmb;


        messages = cmb.readAllMessages();
        if messages == None:
            errormsg = "sim_buster error! error: %s" % cmb.getLastError();
            self.setLastError(errormsg);
            print(errormsg);
            return False;
        for i in messages:
            # todo: optimize, currently repeating open and close per entry
            print("Saving message: %s" % i);
            r = self.__updateRecords(i);
            if not r:
                errormsg = "unknown error";
                self.setLastError(errormsg);
                print(errormsg);
                return False;
        return True;

    def readUnreadMessages(self) -> list:
        with self.__sema:
            db = open(self.__storage_file, "ab+");
            db.seek(0);
            data = cPickle.loads(db.read());
            rVal = list();
            if not data:
                db.close();
                return rVal;
            while data[0]:
                val = data[0].pop(0);
                rVal.append(val);
                data[1].append(val);
            db.truncate(0);
            db.write(cPickle.dumps(data));
            db.close();
            return rVal;

    def readOldMessages(self) -> list:
        with self.__sema:
            data = cPickle.loads(open(self.__storage_file,"rb+").read());
            return data[1];
