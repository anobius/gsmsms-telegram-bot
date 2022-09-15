
import serial, time

from .base import CBase


# todo: IMPLEMENT LOCKING LEL
class CTTYzer(CBase):
    classname = "ttyzer";



    @staticmethod
    def configure_serial(serialport):
        serialport.baudrate =9600;
        serialport.bytesize = serial.EIGHTBITS;
        serialport.parity = serial.PARITY_NONE;
        serialport.stopbits = serial.STOPBITS_ONE;
        serialport.xonxoff = False;
        serialport.rtscts = False;
        serialport.dsrdtr = False;
        serialport.writeTimeout = 2;
        serialport.timeout = 10;
        #return serialport;

    def __init__(self ,tty_port: str):
        self.tty = tty_port;
        self.__initialize_serial();

    def __initialize_serial(self):
        print("Opening serial port at %s" % self.tty);
        # todo: optimize init
        a = serial.Serial();
        a.port =self.tty;
        self.configure_serial(a);

        self.__ser = a;
        a.open();
        a.flushInput();
        a.flushOutput();

    def reinitializePort(self):
        oldobj = self.__ser;
        oldobj.close();
        a = serial.Serial();
        a.port =self.tty;
        self.configure_serial(a);
        a.open();
        a.flushInput();
        a.flushOutput();
        self.__ser = a;
        del oldobj;
        print("%s reinitialized" % self.tty);
        return 1;


    def sendcommand(self ,command: str, read_until : str = None) -> str:
        #print("Sending AT command: %s" % command);
        a = self.__ser;
        sendcommand = str(command + "\r\n").encode('utf-8');
        read_until = read_until.encode('utf-8');
        a.write(sendcommand);
        # temporary, find a limiter properly
        # return a.read_all().replace(command,"",1).strip();
        if not read_until:
            time.sleep(1)
            return a.read_all().decode('utf-8').replace(command ,"" ,1).strip();
        else:
            return a.read_until(read_until).decode('utf-8').replace(command ,"" ,1).strip();

    def __del__(self):
        self.__ser.close();