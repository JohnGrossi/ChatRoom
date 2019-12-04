import socket
import select
import errno
import sys
import re
from datetime import datetime
import time
import argparse



class IRCBot(object):

    #set up all bot variables
    def __init__(self, ip = "127.0.0.1", user = "Bot", name = "Bot", nick = "Bot", channel = ""):
        self.ip = ip
        self.port = 6667
        self.nickname = nick
        self.name = name
        self.user = user
        self.channel = channel
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rec_buffer = ""
        self.line_regex = re.compile(r"\r?\n")
        self.test = True

    #connect to server socket
    def connect(self):
        self.socket.connect((self.ip, self.port))
        self.socket.setblocking(False)
        self.send_msg("USER " + self.user + " " + self.user + " " + self.user + " :" + self.name)
        self.send_msg("NICK " + self.nickname)
        if (self.channel != ""):
            self.send_msg("JOIN #" + self.channel)

    #send message
    def send_msg(self, msg):
        print(">>> " + msg)
        self.socket.send((msg + "\r\n").encode())

    #recieve message
    def recieve(self):
        try:
            self.rec_buffer += self.socket.recv(1000).decode()

        except IOError as e:
            # This is normal on non blocking connections - when there are no incoming data error is going to be raised
            # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
            # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
            # If we got different error code - something happened                                                              (is this coppied or did this get typed) -john
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

    #empty buffer
    def buffer_empty(self):
        if(self.rec_buffer == ""):
            return True

    #takes whatever is in the buffer, splits it up then calls command handler
    def parse_buffer(self):
        lines = self.line_regex.split(self.rec_buffer)
        self.rec_buffer = lines[-1]
        lines = lines[0:-1]
        for line in lines:

            if (not line):
                continue

            line_split = {}
            command_args = {}
            msg = ""

            print("<<< " + line)

            if (line.find(":") != -1):
                line_split = line.strip(":").split(":")

                command_args = line_split[0].strip(" ").split(" ")

                if (len(line_split) > 1):
                    msg = line_split[-1]

            self.handle_command(command_args,msg)

    #command handler for all commands
    def handle_command(self, args, msg):
        command = ""

        if (len(args) == 1):
            command = args[0]
        elif (len(args) >= 2):
            command = args[1]
        else:
            return

        #method to repond to ping
        def pong_handler():
            self.send_msg("PONG :" + msg)

        #method to send private message
        def privmsg_handler():
            msg_from = args[0].split("!")[0]
            if(re.match("#", args[2])):
                print(msg_from + "> " + args[2] + ": " + msg)

                if (re.match("!", msg)):

                    def bot_time():
                        self.send_msg("PRIVMSG " + args[2] + " :" + str(datetime.time(datetime.now())))

                    def bot_day():
                        day = datetime.datetime.now()
                        self.send_msg("PRIVMSG " + args[2] + " :" + day.strftime("%A"))

                    bot_commands = {
                        "!time": bot_time,
                        "!day": bot_day
                    }

                    try:
                        bot_commands[msg]()
                    except KeyError:
                        print("not a valid command")

            else:
                print(msg_from + ": " + msg)
                self.send_msg("PRIVMSG " + msg_from + " :this is a :test")

        #switch case to call relevant command
        command_handlers = {
            "PING": pong_handler,
            "PRIVMSG": privmsg_handler
        }

        try:
            command_handlers[command]()
        except KeyError:
            return

    #stats connection, loops till it recieves messages, pareses them then does relevant command
    def run(self):
        self.connect()
        while True:
            self.recieve()
            if(not self.buffer_empty()):
                self.parse_buffer()

#main method, gives bot options
def main():
    parser = argparse.ArgumentParser(description = "A bot for the irc protocol")
    parser.add_argument('--server', help="server to connect to (default = '127.0.0.1')", default = "127.0.0.1")
    parser.add_argument('--nick', help="nickname to use on the server (default = 'Bot')", default = "Bot")
    parser.add_argument('--user', help="username to use on the server (default = 'Bot')", default = "Bot")
    parser.add_argument('--name', help="real name to use on the server (default = 'Bot')", default = "Bot")
    parser.add_argument('--channel', help="channel to connect to on the server (none by default)", default = "")

    print("\n ___ ___  ___ ___      _ ")
    print("|_ _| _ \\/ __| _ ) ___| |_ ")
    print(" | ||   / (__| _ \\/ _ \\  _|")
    print("|___|_|_\\\\___|___/\\___/\\__|\n")

    args = parser.parse_args()

    bot = IRCBot(ip = args.server, user = args.user, name = args.name, nick = args.nick, channel = args.channel)
    bot.run()

#runs main method
if __name__ == "__main__":
    main()
