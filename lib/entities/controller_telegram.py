import _pickle as cPickle
import threading
import time
import telegram
import yaml
import os

from .transcriber_base import CTranscriber

from ..shared.log import getlasterrortraceback

_CHAT_REGISTER = "This chat now receives sms updates!"
_CHAT_DEREGISTER = "This chat has opted out of receiving sms updates."

class CControllerTelegram(CTranscriber):

    classname = "controller_telegram";

    def __init__(self, bot_token : str, registrants_file : str = "/tmp/rgstrr.pickol", privilege_file : str = "/tmp/rgstrr_priv.yml"):
        self.bot_token = bot_token;
        self.__r_file = registrants_file;
        self.__is_active = False;
        self.__p_file = privilege_file;
        self.__sema = threading.BoundedSemaphore();

        super().__init__();

    def _initialize_files(self):
        if not os.path.isfile(self.__p_file):
            f = open(self.__p_file,"wb+");
            f.write(b"[]");
            f.close();
        if not os.path.isfile(self.__r_file):
            f = open(self.__r_file,"wb+");
            f.write(cPickle.dumps([]));
            f.close();

    def start(self) -> bool:
        if self.__is_active: return False;
        self.__is_active = True;
        # start thread
        self.__t = threading.Thread(target=self.__loop);
        self.__t.start();
        return True;

    def stop(self) -> bool:
        if not self.__is_active: return False;
        self.__is_active = False;
        self.__t.join();
        del self.__t;
        self.__t = None;
        return True;

    def __del__(self):
        print("killing registerer (%s)" % str(self));
        self.stop();

    def __loop(self):
        asd = telegram.Bot(self.bot_token);
        curr_offset = 0;
        while self.__is_active:
            try:
                curr_offset = self.__getTelegramUpdates(asd ,curr_offset)  ;  # possibly fix timeout issues
            except:
                print(getlasterrortraceback());
            time.sleep(1);

    def getRegistrants(self) -> list:
        data = cPickle.loads(open(self.__r_file,"rb+").read());
        return data;

    def getAdminList(self) -> list:
        try:
            raw_data = open(self.__p_file).read();
            data = yaml.load(raw_data,Loader=yaml.FullLoader);
            FAIL = "privileges file not well-formed, should be standard list";
            assert type(data) == list, FAIL;
            self.setLastError(FAIL);
            return data;
        except Exception as e:
            print("Error reading privileges file: %s!" % e);
            return [];

    def registerId(self, chat_id : int, username : str) -> bool:
        while self.__sema:
            print("Registering chat from user: %s [%s]" % (username ,chat_id));
            db = open(self.__r_file ,"ab+");
            # data format: [(chat_id,username)]
            db.seek(0);
            data = cPickle.loads(db.read());
            to_put = (chat_id ,username);
            if to_put in data:
                db.close();
                self.setLastError("User already exists!")
                return False;
            data.append(to_put);
            db.truncate(0);
            db.write(cPickle.dumps(data));
            db.close();
            return True;


    def unregisterId(self, chat_id : int, username : str) -> bool:
        while self.__sema:
            print("Unregistering chat from user: %s [%s]" % (username ,chat_id));
            db = open(self.__r_file ,"ab+");
            # data format: [(chat_id,username)]
            db.seek(0);
            data = cPickle.loads(db.read());
            to_put = (chat_id ,username);
            if to_put not in data:
                db.close();
                self.setLastError("User does not exist!")
                return False;
            data.remove(to_put);
            db.truncate(0);
            db.write(cPickle.dumps(data));
            db.close();
            return True;


    def __getTelegramUpdates(self, asd ,offset=None) -> int:

        __command_list = {
            "/start": lambda *args: self.registerId(*args[:2]) and asd.sendMessage(args[0], _CHAT_REGISTER),
            "/stop": lambda *args: self.unregisterId(*args[:2]) and asd.sendMessage(args[0], _CHAT_DEREGISTER),
            "__UNKNOWN": lambda *args: asd.sendMessage(args[0], "Invalid command")
        }

        updates = asd.get_updates(offset=offset ,timeout=10)
        for i in updates:
            #todo: handle message types from chat migrations from group hierarchy changes
            #  i.message.migrate_from_chat_id
            #  i.message.migrate_to_chat_id
            #print(i)
            offset =i.update_id;
            if not i.effective_chat: #case for update not having chat info
                continue;

            from_chat_id = i.effective_chat.id;
            if i.effective_chat.title:  # if group
                metadata = "[" + str(from_chat_id) + "]G:" + i.effective_chat.title;
            else:
                metadata = "[" + str(from_chat_id) + "]DIRECT:%s.%s" % \
                (i.effective_chat.first_name, i.effective_chat.last_name);

            # check if edited message
            if i.edited_message:
                sample = i.edited_message;
            else:
                sample = i.message;

            if not sample: #if update received is not related to messages
                continue;

            name = sample.from_user.name #todo: username filter
            text = sample.text
            datestr = sample.date.strftime("%Y-%m-%d %H:%M:%S %Z");
            print("%s (%s) %s: %s" % (datestr, metadata, name, text));
            if sample.reply_to_message:
                rname = sample.reply_to_message.from_user.name
                rtext = sample.reply_to_message.text
                rdatestr = sample.reply_to_message.date.strftime("%Y-%m-%d %H:%M:%S %Z")
                print("\t REPLY TO:: %s %s: %s" % (rdatestr, rname, rtext));

            # registering starts here:
            if not text:
                continue;
            #available commands if admin
            if text[0] == '/' and name in self.getAdminList():
                lcommandstring = text.split(' ');
                command_name = lcommandstring[0].lower();
                __command_list.setdefault(command_name,__command_list['__UNKNOWN']);
                __command_list[command_name](from_chat_id, name, lcommandstring[1:]);
            else:#commands here for non-admin
                pass;

        if not updates:
            return offset;
        return (offset + 1);

    def broadcastMessage(self, message):
        instance = telegram.Bot(self.bot_token);
        for j in self.getRegistrants():
            print("Sending message to %s(%s)\nMessage:\n%s" % (j[1], j[0], message));
            instance.sendMessage(j[0], message);


