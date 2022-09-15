import threading
import time
import hashlib

from .ttyzer import CTTYzer

from ..shared.decoder import UCS2

# todo: filter results
class CMBuster(CTTYzer):
    classname = "sim_buster";

    def __init__(self, *args,**kwargs):
        self.__sema = threading.BoundedSemaphore();
        super().__init__(*args,**kwargs);

        self.__initialize_sim800c();

        # INIT AS AT+CSCS="UCS2"
        # AND AT+CMGF=1 (TEXT MODE)
        # POSSIBLY RESET WITH AT+CFUN=0 THEN AT+CFUN=1 OR AT+CFUN=1,1

    def __initialize_sim800c(self):
        print("Initializing text mode @ %s" % self.tty);
        self.sendcommand("AT+CSCS=\"UCS2\"");
        self.sendcommand("AT+CMGF=1");
        self.sendcommand("AT+CPMS=\"ME\",\"ME\",\"ME\""); #STORE SHIT IN MEMORY GOGO IOPS
        self.sendcommand("AT+CNMI=0,0,0,0,0"); #disable unsolicited sms notifications, screws up the buffer


    def checkStatus(self) -> bool:
        with self.__sema:
            result = self.sendcommand("AT");
            if "OK" in result:
                return True;
            return False;

    def __reformat_raw_texts_all(self, string: str) -> list:
        # format [(index,message status,sender number,sender something,date,sms body)]

        string = string[:-2];  # remove "OK" from message

        ts = string.split("+CMGL: ");
        rVal = list();
        for i in ts[1:]:
            a = i.split('\n', 1)
            body = a[1].strip();
            metadata = a[0].replace('"', '').split(',', 4);
            try:
                body = UCS2.decode(body);
                metadata[2] = UCS2.decode(metadata[2]);
            except Exception as e:
                print(e);
                pass;
            rVal.append(tuple([i.strip() for i in metadata] + [body]));
        return rVal

    def readAllMessages(self, delete_after: bool = True) -> list:
        with self.__sema:
            # todo: relocate this signal quality check elsewhere.. maybe?
            while 1:
                try:
                    signal, error_rate = self.getSignalQuality();  # check signal quality, any signs of network disconnections
                    break;
                except: #usb failure case here
                    print("Reinitializing serial port");
                    self.reinitializePort();

            if signal == 0:
                print("Disconnected from network, attempting to reset.");
                while not self.__attemptNetworkReconnect():
                    print("Failure, retrying indefinitely..");
                print("Connection re-established!");

            #print("Getting all messages from sim");
            result = self.sendcommand("AT+CMGL=\"ALL\"");
            #todo: GET ONLY LINE WITH +CMGL
            if "ERROR" in result[-5:]:
                print("[%s] Message Read Failure" % self.tty);
                self.__initialize_sim800c();
                self.setLastError("Message Read Failure");
                return None;
            result.replace("OK","") and print("RAW MESSAGE: %s" % result);
            data = self.__reformat_raw_texts_all(result);
            #hide
            messages = [{"sender": i[2] if hashlib.md5(i[2].encode('utf-8')).hexdigest() != '89c37f51a5e5a27737b51ab343f3018e' else "<REDACTED>", "date": i[4], "message": i[5]} for i in data if i[1] == "REC UNREAD"]

            # POSSIBLE CONCURRENCY ISSUE.
            if delete_after:
                #result = self.sendcommand("AT+CMGD=1,1");
                result = self.sendcommand("AT+CMGD=41,1"); #41 is the starting possible value for ME storage indices
                if "ERROR" in result[-5:]:
                    print("Message deletion failure");
                    self.setLastError("Message Deletion Failure");

            return messages;

    def getServiceProvider(self) -> str:
        result = self.sendcommand("AT+COPS?"); #todo: longer than 1 second, pexpect method will fix
        return result;

    def getSignalQuality(self) -> tuple:
        rawmsg = self.sendcommand("AT+CSQ");
        a = rawmsg.find("+CSQ");
        b = a + rawmsg[a:].find("\n");
        result = tuple([int(i) for i in rawmsg[a+6:b].split(',')]);
        return result;

    def setAirplaneMode(self, value : bool) -> bool:
        with self.__sema:
            if value:
                self.sendcommand("AT+CFUN=0");
                time.sleep(5); #todo: pexpect method instead of wait
            else:
                self.sendcommand("AT+CFUN=1");
            return True

    def __attemptNetworkReconnect(self,check_count : int = 30) -> bool:
        self.sendcommand("AT+CFUN=0");
        time.sleep(5); #todo: pexpect method instead of wait
        self.sendcommand("AT+CFUN=1");

        rVal = False;
        for i in range(0,check_count):
            signal,error_rate=self.getSignalQuality();
            if signal != 0:
                rVal = True;
                break;
            time.sleep(1);
        return rVal;

    def sendcommand(self ,command: str,**kwargs) -> str:
        return super().sendcommand(command,read_until="\nOK");


