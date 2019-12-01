import socket
import select
import re
import sys

# #all set up
#
# HEADER_LENGTH = 10
#
# IP = "127.0.0.1"
# PORT = 6667
#
# # Create a socket
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# #allow re-conect
# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#
# # Bind, so server informs operating system that it's going to use given IP and port
# server_socket.bind((IP, PORT))
#
# # This makes server listen to new connections
# server_socket.listen()

class Client(object):
    #add people
    #remove people

    #set up all client variables etc
    def __init__(self, server, socket):
        self.server = server
        self.socket = socket
        self.writeBuffer = ""
        self.rec_buffer = ""
        self.nick = ""
        self.name = ""
        self.user = ""
        self.registered = False
        self.line_regex = re.compile(r"\r?\n")
        #etc

    #for testing
    def get_connection(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("127.0.0.1",6667))
        while True:
            # Wait for a connection
            print('waiting for a connection')
            self.socket.listen()
            connection, client_address = self.socket.accept()
            self.socket = connection
            break

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
            command_args = {}
            msg = ""

            print("<<< " + line)

            if (line.find(":") != -1):
                line_split = line.strip(":").split(":")
                command_args = line_split[0].strip(" ").split(" ")
                if (len(line_split) > 1):
                    command_args = command_args + [line_split[-1]]
            else:
                command_args = line.strip(" ").split(" ")

            #print(str(command_args) + " > " + msg)
            if(self.registered):
                self.handle_command(command_args)
            else:
                self.register_client(command_args)

    def register_client(self,args):
        if(args[0] == "USER"):
            if(len(args) < 5):
                ERR_NEEDMOREPARAMS(args[0])
                return

            self.name = args[-1]
            self.user = [1]
        if(args[0] == "NICK"):
            if(len(args) < 2):
                ERR_NEEDMOREPARAMS(args[0])
                return
            # if(self.server.check_nick_collision(args[1])): #need to implement
            #     return
            self.nick = args[1]

        if(self.nick != "" and self.user != ""):
            self.registered = True
            #self.message("registered")
            #self.send_reg_replies() #need to implement




    def handle_command(self, args):
        print(args)
        command = args[0]
        print(command + " > " + str(args))

        #def all commands, ie join, privmsg etc
        def join():
            print("join")

        def part():
            print("part")

        def nick():
            print("nick")

        def list():
            print("list")

        def privmsg():
            print("privmsg")

        #def notice():

        def ping():
            print("ping")

        def pong():
            print("pong")

        def wallops():
            print("wallops")

        def who():
            print("who")

        def topic():
            print("topic")

        def quit():
            print("quit")


        command_handlers = {    #switch on commands
        "JOIN" : join, #calls join handler
        "PART" : part,
        "NICK" : nick,
        "LIST" : list,
        "PRIVMSG" : privmsg,
        "NOTICE" : privmsg,
        "PING" : ping,
        "PONG" : pong,
        "WALLOPS" : wallops,
        "WHO" : who,
        "TOPIC" : topic,
        "QUIT" : quit
        #default 421?
        }

        try:
            command_handlers[command]()
        except KeyError:
            print("no handler for command/ reply number")

    def socket_readable(self):
        try:
            self.rec_buffer += self.socket.recv(1000).decode()
            #print(self.rec_buffer)

        except IOError as e:
                # This is normal on non blocking connections - when there are no incoming data error is going to be raised
                # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
                # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
                # If we got different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

    def message(self, message):
        #self.writeBuffer += message + "\r\n"
        self.socket.send((message + "\r\n").encode())
        print(message)

    def reply(self, message):
        self.message(": %s %s" % (self.server, message))

    #Error Replies:
    def ERR_NOSUCHNICK(self, nickname):
        self.reply("401 %s :No such nick/channel" % nickname)

    def ERR_NOSUCHCHANNEL(self, channel):
        self.reply("403 %s :No such channel" % channel)

    def ERR_UNKNOWNCOMMAND(self, command):
        self.reply("421 %s :Unknown command" % command)

    def ERR_NONICKNAMEGIVEN():
        self.reply("431 :No nickname given")

    def ERR_NICKNAMEINUSE(self, nickname):
        self.reply("433 %s :Nickname is already in use" % nickname)

    def ERR_USERNOTINCHANNEL(self, nickname, channel):
        self.reply("441 %s %s :They aren't on that channel" % (nickname, channel))

    def ERR_NEEDMOREPARAMS(self, command):
        self.reply("461 %s :Not enough parameters" % command)

    #Command responses:
    #RPL_TOPIC, etc

class Server(object):

    def __init__(self):
        self.channels = {}
        self.clients = {}
        self.nicknames = {}
        self.port = 6667
        self.ip = "127.0.0.1"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rec_buffer = ""
        self.line_regex = re.compile(r"\r?\n")



class Channel(object):
    def __init__(self, name):
        self.name = name
        self.members = {}
        self._topic = ""
        #add people
        #remove people



client = Client("","")
client.get_connection()
while True:
    client.socket_readable()
    if(not client.buffer_empty()):
        client.parse_buffer()
