import socket
import select
import errno
import sys
import re
from datetime import datetime
import time
import argparse

class Client(object):
    #set up all client variables
    def __init__(self, client_socket, server):
        self.socket = client_socket
        self.server = server
        self.channels = {}
        self.host, self.port = client_socket.getpeername()
        self.hostname = socket.getfqdn(self.host)
        self.write_buffer = ""
        self.rec_buffer = ""
        self.nick = ""
        self.name = ""
        self.user = ""
        self.registered = False
        self.line_regex = re.compile(r"\r\n")
        self.last_recieve = time.time()
        self.ping_sent = False

    #returns the sender details for this client
    def sender(self):
        return "%s!%s@%s" % (self.nick,self.user,self.hostname)

    #checks if the buffer is empty
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
                while len(line_split) > 2:
                    line_split[-2] += ":" + line_split[-1]
                    line_split = line_split[:-1]
                command_args = line_split[0].strip(" ").split(" ")

                if (len(line_split) > 1):
                    command_args = command_args + [line_split[-1]]
            else:
                command_args = line.strip(" ").split(" ")

            if(self.registered):
                self.handle_command(command_args)
            else:
                self.register_client(command_args)

    #method called if its a new client, sets up name, nick ect
    def register_client(self,args):
        if(args[0] == "USER"):
            if(len(args) < 5):
                self.ERR_NEEDMOREPARAMS(args[0])
                return

            self.name = args[-1]
            self.user = args[1]
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

    #welcome messages when first connected and registration is complete
    def send_reg_replies(self):
        self.RPL_WELCOME()
        self.RPL_YOURHOST()
        self.RPL_CREATED()
        self.RPL_MYINFO()
        self.RPL_LUSERCLIENT()
        self.ERR_NOMOTD()

    #command handler for all commands
    def handle_command(self, args):
        command = args[0]

        #method to join channel
        def join():
            if len(args) < 2 :
                self.ERR_NEEDMOREPARAMS("JOIN")
                return
            if (args[1].find("#") != -1):
                channel = args[1].strip("#")
            if (channel in self.server.channels.keys()):
                self.server.channels[channel].members[self.nick] = self
                self.channels[channel] = self.server.channels[channel]

            else:
                self.server.channels[channel] = Channel(channel)
                self.server.channels[channel].members[self.nick] = self
                self.channels[channel] = self.server.channels[channel]
            print(self.channels.keys())
            print(self.channels.values)

            for client in self.channels[channel].members.values():
                client.reply("JOIN", "", self.sender(), "#%s"%channel)

            self.reply("332",":this is a channel topic", channel =  channel)

            members = ""
            for client in self.channels[channel].members.values():
                members += " %s" % client.nick
            self.reply("353","= #%s :@%s" % (channel, members))
            self.reply("366",":End of NAMES list", channel = channel)

        #method to leave channel
        def part():
            if len(args) < 2 :
                self.ERR_NEEDMOREPARAMS("PART")
                return
            channel_names = args[1:-1]
            print(args)
            for name in channel_names:
                name = name.strip("#")
                print(name)
                print(self.channels.keys())
                if name in self.channels.keys():
                    del self.channels[name] #remove channel from client's dictionary
                    del self.server.channels[name].members[self.nick] #remove client from dictionary of channel members
                else:
                    if name in self.server.channels.keys():
                        self.ERR_NOTONCHANNEL(name)
                    else:
                        self.ERR_NOSUCHCHANNEL(name)

        #method to set nickname
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

        #method to list channels and their topics
        def list():
            if len(args) < 2:
                if len(self.server.channels) < 1: #if there are no channels
                    self.RPL_LISTSTART()
                    self.RPL_LISTEND()
                    return
                #list all channels and their topics
                for channel_name in self.server.channels.keys():
                    channel = self.server.channels.get(channel_name)
                    self.RPL_LISTSTART()
                    self.RPL_LIST(channel_name, channel._topic)
                    self.RPL_LISTEND()
            else:
                #list topics of given channels
                channel_names = args[1:-1]
                for name in channel_names:
                    if name in self.channels.keys():
                        channel = self.server.channels.get(channel_name)
                        self.RPL_LISTSTART()
                        self.RPL_LIST(channel_name, channel._topic)
                        self.RPL_LISTEND()


        #method to preform private message
        def privmsg():
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
                if (reciever.find("#") != -1):
                    channel = reciever.strip("#")
                    if (channel in self.channels.keys()):
                        for client in self.channels[channel].members.values():
                            if(client != self):
                                client.reply("PRIVMSG",":%s"%message,self.sender(),channel = channel)
                    else:
                        self.ERR_NOSUCHNICK(channel)
                        return
                else:
                    if (reciever in self.server.nicknames.keys()):
                        self.server.nicknames[reciever].reply("PRIVMSG",":%s"%message,self.sender())
                    else:
                        self.ERR_NOSUCHNICK(reciever)
                        return

        #ping and pong method
        def pong():
            self.ping_sent = False
        def ping():
            if len(args) < 2:
                self.ERR_NOORIGIN()
            else:
                self.reply("PONG", ":%s" % args[1])

        #method to set topic
        def topic():
            if len(args) < 2:
                self.ERR_NEEDMOREPARAMS("TOPIC")
                return
            channel_name = args[1];
            if channel_name not in self.channels.keys():
                self.ERR_NOTONCHANNEL(channel_name)
                return
            channel = self.channels.get(channel_name)
            if len(args) == 2:
                if channel._topic is None:
                    self.RPL_NOTOPIC(channel_name)
                else:
                    self.RPL_TOPIC(channel)
            else:
                #set new topic
                new_topic = args[2]
                channel._topic = new_topic

        #Method to leave server
        def quit(self, arguments):
            if len(arguments) == 0:
                quitMsg = self.nickname
            else:
                quitMsg = arguments[0]
            self.disconnect(quitMsg)

        #dictionary that contains all relevant commands
        command_handlers = {
        "JOIN" : join,
        "PART" : part,
        "NICK" : nick,
        "LIST" : list,
        "PRIVMSG" : privmsg,
        "PING" : ping,
        "PONG" : pong,
        "TOPIC" : topic,
        "QUIT" : quit
        }

        try:
            command_handlers[command.upper()]()
        except KeyError:
            print("no handler for command/ reply number")
            self.ERR_UNKNOWNCOMMAND(command)

    #reads whatever is coming from socket into buffer
    def socket_readable(self):
        read_data = ""
        try:
            read_data = self.socket.recv(1000)
            self.rec_buffer += read_data.decode()
            self.last_recieve = time.time()
            self.parse_buffer()
        except socket.error as e:
            read_data = ""

        if not read_data:
            self.disconnect("connection died")

    #checks if other side is still there, using ping and pong
    def check_connected(self):
        if (self.last_recieve + 45 < time.time()):
            if (self.ping_sent and self.last_recieve + 60 < time.time()):
                self.disconnect("no response to ping")
            else:
                self.message("PING :" + self.server.hostname)
                self.ping_sent = True

    #called when the client disconnecs, eg. if no response from ping
    def disconnect(self, message):
        self.reply("QUIT", ":%s" % message)
        del self.server.clients[self.socket]
        if (self.nick in self.server.nicknames):
            del self.server.nicknames[self.nick]
        for channel in self.channels.values():
            del channel.members[self.nick]
        self.socket.close()
        #remove client & close socket

    #writes message to buffer
    def message(self, message):
        self.write_buffer += (message + "\r\n")
        print(">>> " + message)

    #writes to socket
    def socket_write(self):
        try:
            sent = self.socket.send(self.write_buffer.encode())
            self.write_buffer = self.write_buffer[sent:]
        except socket.error as e:
            self.disconnect("socket error")

    #reply message with sender, command, nick and message
    def reply(self, command, message = "", sender = "", nick = "", channel = ""):
        if (sender == ""):
            sender = self.server.hostname
        if (channel != "" and channel.find("#") == -1):
            channel = "#%s" % channel
        if (nick == "" and channel == ""):
            nick_channel = self.nick
        elif(nick == "" or channel == ""):
            nick_channel = "%s%s" % (nick, channel)
        else:
            nick_channel = "%s %s" % (nick, channel)
        self.message(":%s %s %s %s" % (sender, command, nick_channel, message))

    #Error Replies:
    def ERR_NOSUCHNICK(self, nickname):
        self.reply("401", "%s :No such nick/channel" % nickname)

    def ERR_NOSUCHCHANNEL(self, channel):
        self.reply("403", ":No such channel" % channel)

    def ERR_NOORIGIN(self):
        self.reply("409", ":No origin specified")

    def ERR_UNKNOWNCOMMAND(self, command):
        self.reply("421", "%s :Unknown command" % command)

    def ERR_NOMOTD(self):
        self.reply("422", ":no MOTD")

    def ERR_NONICKNAMEGIVEN(self):
        self.reply("431", ":No nickname given")

    def ERR_ERRONEUSNICKNAME(self):
        self.reply("432", ":Erroneus nickname")

    def ERR_NICKNAMEINUSE(self):
        self.reply("433", ":Nickname is already in use")

    def ERR_USERNOTINCHANNEL(self, channel):
        self.reply("441", "%s :They aren't on that channel" % (channel))

    def ERR_NOTONCHANNEL(self, channel_name):
        self.reply("442", "%s :You're not on that channel" % channel_name)

    def ERR_NEEDMOREPARAMS(self, command):
        self.reply("461", "%s :Not enough parameters" % command)

    #Numeric replies
    def RPL_WELCOME(self):
        self.reply("001", ":Welcome")

    def RPL_YOURHOST(self):
        self.reply("002", ":Your host is %s, running version thisIRC V0.1" % self.server.hostname)

    def RPL_CREATED(self):
        self.reply("003", ":the server was created sometime")

    def RPL_MYINFO(self):
        self.reply("004", "%s version 0 0" % self.server.hostname)

    def RPL_LUSERCLIENT(self):
        self.reply("251", ":there are %d users" % len(self.server.clients))

    def RPL_LISTSTART(self):
        self.reply("321", "Channel :Users Name")
    
    def RPL_LIST(self, channel_name, topic):
        self.reply("322", "%s :%s" % (channel_name, topic))
    
    def RPL_LISTEND(self):
        self.reply("323", ":End of /LIST")

    def RPL_NOTOPIC(self, channel_name):
        self.reply("331", "%s :No topic is set" % channel_name)

    def RPL_TOPIC(self, channel):
        self.reply("331", "%s :%s" % (channel.name, channel._topic))

class Server(object):
    #set up all Server variables
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

    #set up socket connection
    def connect_socket(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip, self.port))
        self.socket.listen()

    #run server
    def run(self):
        #sets up socket
        self.connect_socket()

        runtime = time.time()
        last_check = time.time()

        while True:
            sockets_list = [self.socket]

            for client in self.clients.values():
                sockets_list.append(client.socket)

            #waits for input with 2 second timeout
            read_sockets, write_sockets, exception_sockets = select.select(sockets_list, sockets_list, sockets_list,2)

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

            for notified_socket in write_sockets:
                if notified_socket in self.clients.keys():
                    self.clients[notified_socket].socket_write()


            #tells each client object to ping its connected client every so often
            if (last_check + 10 < time.time()):
                for client in self.clients.values():
                    client.check_connected()
                last_check = time.time()




class Channel(object):
    #set up all channel variables
    def __init__(self, name):
        self.name = name
        self.members = {}
        self._topic = ""

#main method
def main():
    server = Server()
    server.run()

#runs main
if __name__ == "__main__":
    main()
