import socket
import select
import errno
import sys
import re
from datetime import datetime
import time
import argparse

class Client(object):
    #set up all client variables etc
    def __init__(self, client_socket, server):
        self.socket = client_socket
        self.server = server
        self.channels = {}
        self.host, self.port = client_socket.getpeername()
        self.hostname = socket.getfqdn(self.host)
        self.writeBuffer = ""
        self.rec_buffer = ""
        self.nick = ""
        self.name = ""
        self.user = ""
        self.registered = False
        self.line_regex = re.compile(r"\r\n")
        self.last_recieve = time.time()
        self.ping_sent = False
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
                self.ERR_NEEDMOREPARAMS(args[0])
                return

            self.name = args[-1]
            self.user = [1]
        if(args[0] == "NICK"):
            if(len(args) < 2):
                self.ERR_NEEDMOREPARAMS(args[0])
                return
            if(args[1] in self.server.nicknames.keys()):
                self.ERR_NICKNAMEINUSE()
                return
            self.nick = args[1]
            self.server.nicknames[args[1]] = self

        if(self.nick != "" and self.user != ""):
            self.registered = True

            self.send_reg_replies() #need to implement

    def send_reg_replies(self):
        self.RPL_WELCOME()
        self.RPL_YOURHOST()
        self.RPL_CREATED()
        self.RPL_MYINFO()
        self.RPL_LUSERCLIENT()
        self.ERR_NOMOTD()


    def handle_command(self, args):
        #print(args)
        command = args[0]
        #print(command + " > " + str(args))

        #def all commands, ie join, privmsg etc
        def join():
            print("join")

        def part():
            print("part")

            #look at
        def nick():
            if len(args) < 2:
                self.ERR_NONICKNAMEGIVEN()
                return
            newNickname = args[1]

            #check if the new nickname is already in use by a client
            if newNickname not in self.server.nicknames.keys():
                #check if nickname is under the RFC limit
                if len(newNickname) < 9:
                    del self.server.nicknames[self.nick]
                    self.server.nicknames[newNickname] = self
                else:
                    self.ERR_ERRONEUSNICKNAME()
            else:
                self.ERR_NICKNAMEINUSE()

        def list():
            print("list")

        def privmsg():
            print("privmsg")
            if (len(args) < 3):
                self.ERR_NEEDMOREPARAMS("PRIVMSG")
                return

            recievers = []
            message = args[-1]
            #checks for more than 1 reciever
            if (args[1].find(",") != -1):
                recievers = args[1].split(",")
            else:
                recievers = [args[1]]

            for reciever in recievers:
                if (reviever.find("#") != -1):
                    channel = reciever.strip("#")
                    if (channel in self.channels.keys()):
                        for client in self.channels[channel].clients:
                            sender = "%s!%s@%s" % (self.nick,self.user,self.hostname)
                            client.reply("PRIVMSG",message,sender)
                    else:
                        self.ERR_NOSUCHNICK(channel)
                        return
                else:
                    if (reciever in self.server.nicknames.keys()):
                        sender = "%s!%s@%s" % (self.nick,self.user,self.hostname)
                        self.server.nicknames[reciever].reply("PRIVMSG",message,sender)
                    else:
                        self.ERR_NOSUCHNICK(reciever)
                        return







        def pong():
            self.ping_sent = False

        #look at
        def ping():
            if len(args) < 2:
                ERR_NOORIGIN()
            else:
                self.reply("PONG", ":%s" % args[1])

        def wallops():
            print("wallops")

        def who():
            print("who")

        def topic():
            print("topic")

        def quit():
            print("quit")

            #need to edit
        def quit(self, arguments):
            if len(arguments) == 0:
                quitMsg = self.nickname
            else:
                quitMsg = arguments[0]
            self.disconnect(quitMsg)


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
        }

        try:

            command_handlers[command.upper()]()
        except KeyError:
            print("no handler for command/ reply number")
            self.ERR_UNKNOWNCOMMAND(command)

    def socket_readable(self):
        try:
            self.rec_buffer += self.socket.recv(1000).decode()
            self.last_recieve = time.time()
            self.parse_buffer()
            #print(self.rec_buffer)

        except IOError as e:
                # This is normal on non blocking connections - when there are no incoming data error is going to be raised
                # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
                # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
                # If we got different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

    def check_connected(self):
        if (self.last_recieve + 30 < time.time()):
            if (self.ping_sent and self.last_recieve + 60 < time.time()):
                self.disconnect("no response to ping")
            else:
                self.message("PING :" + self.server.hostname)
                self.ping_sent = True


    def disconnect(self, message):
        self.reply("QUIT" ":%s" % message)
        #remove client & close socket

    def message(self, message):
        #self.writeBuffer += message + "\r\n"
        self.socket.send((message + "\r\n").encode())
        print(">>> " + message)

    def reply(self, command, message, sender = ""):
        if (sender == ""):
            sender = self.server.hostname
        self.message(":%s %s %s %s" % (sender, command, self.nick, message))

    #Error Replies:
    def ERR_NOSUCHNICK(self, nickname):
        self.reply("401", "%s :No such nick/channel" % nickname)

    def ERR_NOSUCHCHANNEL(self, channel):
        self.reply("403", ":No such channel" % channel)

    def ERR_NOORIGIN(self):
        self.reply("409", ":No origin specified")

    def ERR_UNKNOWNCOMMAND(self, command):
        self.reply("421", "%s :Unknown command" % command)

    def ERR_NONICKNAMEGIVEN(self):
        self.reply("431", ":No nickname given")

    def ERR_ERRONEUSNICKNAME(self):
        self.reply("432", ":Erroneus nickname")

    def ERR_NICKNAMEINUSE(self):
        self.reply("433", ":Nickname is already in use")

    def ERR_USERNOTINCHANNEL(self, channel):
        self.reply("441", "%s :They aren't on that channel" % (channel))

    def ERR_NEEDMOREPARAMS(self, command):
        self.reply("461", "%s :Not enough parameters" % command)


    def RPL_WELCOME(self):
        self.reply("001", ":Welcome")

    def RPL_YOURHOST(self):
        self.reply("002", ":Your host is %s, running version ShitIRC V0.1" % self.server.hostname)

    def RPL_CREATED(self):
        self.reply("003", ":the server was created sometime")

    def RPL_MYINFO(self):
        self.reply("004", "%s version 0 0" % self.server.hostname)

    def RPL_LUSERCLIENT(self):
        self.reply("251", ":there are %d users" % len(self.server.clients))

    def ERR_NOMOTD(self):
        self.reply("422", ":no MOTD")

    #Command responses:
    #RPL_TOPIC, etc
    #return

class Server(object):

    def __init__(self):
        self.channels = {}
        self.clients = {}
        self.nicknames = {}
        self.port = 6667
        self.ip = "127.0.0.1"
        self.hostname = socket.getfqdn(socket.gethostname())
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rec_buffer = ""
        self.line_regex = re.compile(r"\r?\n")

    def connect_socket(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip, self.port))
        self.socket.listen()

    def run(self):
        # Create a socket, set up, and listening for new connections
        self.connect_socket()


        # List of sockets and clients


        #print("Listening for connections on: " +ip+" Port: "+str(port)+"")
        runtime = time.time()
        last_check = time.time()

        while True:
            sockets_list = [self.socket]

            for client in self.clients.values():
                sockets_list.append(client.socket)

            #waits for input with 2 second timeout
            read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list,2)

                # Iterate over notified sockets
            for notified_socket in read_sockets:
                # If notified socket is a server socket - new connection, accept it
                if notified_socket == self.socket:

                    # Accept new connection
                    client_socket, client_address = self.socket.accept()

                    #
                    self.clients[client_socket] = Client(client_socket,self)


                    # Else existing socket is sending a message
                else:

                    # Tell client it has message to recieve
                    self.clients[notified_socket].socket_readable()

            #tells each client object to ping its connected client every so often
            if (last_check + 15 < time.time()):
                for client in self.clients.values():
                    client.check_connected()
                last_check = time.time()


    def receive_message(client_socket):
        try:
            message_header = client_socket.recv(1000)

            if message_header == 0:
                return False

            # Convert header to int value
            message_length = int(message_header.decode('utf-8').strip())

            # Return an object of message header and message data
            return {'header': message_header, 'data': client_socket.recv(message_length)}

        except:
            return False



class Channel(object):
    def __init__(self, name):
        self.name = name
        self.members = {}
        self._topic = ""
        #add people
        #remove people


# client = Client("","")
# client.get_connection()
# while True:
#     client.socket_readable()
#     if(not client.buffer_empty()):
#         client.parse_buffer()
#


def main():
    server = Server()
    server.run()

if __name__ == "__main__":
    main()
