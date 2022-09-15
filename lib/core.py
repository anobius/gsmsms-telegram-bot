from hashlib import md5

from .entities.sim_buster import CMBuster
from .entities.sim_buster_transcriber_pickler import CSimTranscriberPickler
from .entities.controller_telegram import CControllerTelegram
from .entities.forwarder_telegram import CForwarderTelegram


tomd5sum = lambda strn : md5(bytes(strn,"utf-8")).hexdigest();
class simbastor(object):
    def __init__(self, telegram_bot_token : str,  tty_location : str = "/dev/ttyUSB0", registrants_file : str = "/tmp/registry-#TOKEN#.pickle", message_storage_file : str = "/tmp/messages-#TOKEN#.pickle", privilege_file : str = "/tmp/registry_privileged-#TOKEN#.yml"):

        #append the token, chat_id's may not work with different bots
        tokenmd5 = tomd5sum(telegram_bot_token);
        registrants_file = registrants_file.replace("#TOKEN#",tokenmd5)
        message_storage_file = message_storage_file.replace("#TOKEN#",tokenmd5)
        privilege_file = privilege_file.replace("#TOKEN#",tokenmd5)

        print("Node1:\n\tToken: %s\n\tregistry file: %s\n\tmessage storage file: %s\n\tprivileges file: %s\n" % (telegram_bot_token,registrants_file,message_storage_file,privilege_file));

        sim_communicator = CMBuster(tty_location);
        sim_transcriber = CSimTranscriberPickler(sim_communicator, message_storage_file);
        telegram_message_parser = CControllerTelegram(telegram_bot_token, registrants_file, privilege_file);
        telegram_forwarder = CForwarderTelegram(sim_transcriber,telegram_message_parser);

        #start parser thread for auto-adding of users for receiving sms
        telegram_message_parser.start();
        #start forwarder thread to start actually reading  from the gsm module
        telegram_forwarder.start();



