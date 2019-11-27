import socket
import select
import errno
import sys
import re


class IRCBot(object):
    

    def __init__(self, ip, user = "Bot", name = "Bot", nick = "Bot", channel = ""):
        self.ip = ip
        self.port = 6667
        self.nickname = nick
        self.name = name
        self.user = user
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rec_buffer = ""
        self.line_regex = re.compile("\r?\n")
        self.test = True

        

    def connect(self):
        self.socket.connect((self.ip, self.port))
        self.socket.setblocking(False)
        self.send_msg("USER " + self.user + " " + self.user + " " + self.user + " :" + self.name)
        self.send_msg("NICK " + self.nickname)
        self.send_msg("JOIN #test")

    def send_msg(self, msg):
        self.socket.send((msg + "\r\n").encode())

    def recieve(self):
        try:
            self.rec_buffer += self.socket.recv(1000).decode()
            print(self.rec_buffer)


        except IOError as e:
                # This is normal on non blocking connections - when there are no incoming data error is going to be raised
                # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
                # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
                # If we got different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()


    def buffer_empty(self):
        if(self.rec_buffer == ""):
            return True

    def parse_buffer(self):
        lines = self.line_regex.split(self.rec_buffer)
        self.rec_buffer = lines[-1]
        lines = lines[0:-1]
        for line in lines:

            if (not line):
                continue

            line_split = {}
            line_commands = {}
            line_arguments = {}
            command = ""
            msg = ""
            msg_from = ""

            if (line.find(":") != -1):
                line_split = line.split(":")

                if (line_split[0] == ""):
                    line_split = line_split[1:]

                if (len(line_split) > 1):
                    msg = line_split[-1]

                if (line_split[0].find(" ") != -1):
                    line_arguments = line_split[0].split(" ")

                    if (len(line_arguments) > 1):
                        command = line_arguments[1]
                        







  



    def testqwe(self):
        if(self.test):
            self.send_msg("PRIVMSG bot4 :test")
            self.test = False


    def run(self):
        self.connect()
        while True:
            self.testqwe()
            self.recieve()
            if(not self.buffer_empty()):
                self.parse_buffer()




bot = IRCBot("127.0.0.1", "bot2", "bot3", "bot4")
bot.run() 






