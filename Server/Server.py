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
    def init(self, server, socket):
        self.server = server
        self.socket = socket
        self.realName = None
        self.nickname = None
        self.writeBuffer = ""
        #etc


    def join(self, arguments):

    def part(self, arguments):

    def nick(self, arguments):
        if len(arguments) == 0:
            ERR_NONICKNAMEGIVEN()
            return
        newNickname = arguments[0]

        #check if the new nickname is already in use by a client
        client = server.getClient(newNickname)
        if client is None:
            #check if nickname is under the RFC limit
            if len(arguments[0]) < 9:
                #change in server dictionary etc
            else:
                ERR_ERRONEUSNICKNAME()
        else:
            ERR_NICKNAMEINUSE()




    def listHandler(self, arguments):

    def privmsg(self, arguments):

    #def notice(self, arguments):

    def ping(self, arguments):
        if len(arguments) == 0:
            ERR_NOORIGIN()
        else:
            self.reply("PONG %s" % arguments[0])

    def pong(self, arguments):
        pass

    def wallops(self, arguments):

    def who(self, arguments):

    def topic(self, arguments):

    def quit(self, arguments):
        if len(arguments) == 0:
            quitMsg = self.nickname
        else:
            quitMsg = arguments[0]
        self.disconnect(quitMsg)

    def commandHandler(self, command, arguments):
        commands = {
        "JOIN" : join
        "PART" : part
        "NICK" : nick
        "LIST" : listHandler
        "PRIVMSG" : privmsg
        "NOTICE" : privmsg
        "PING" : ping
        "PONG" : pong
        "WALLOPS" : wallops
        "WHO" : who
        "TOPIC" : topic
        "QUIT" : quit
        }

        try:
            commands[command](self, arguments)
        except KeyError:
            self.ERR_UNKNOWNCOMMAND()


    def disconnect(self, message):
        self.reply("QUIT :%s" % message)
        #remove client & close socket

    def message(self, message):
        self.writeBuffer += message + "\r\n"

    def reply(self, message):
        self.message(":%s %s" % (self.server, message))

    #Error Replies:
    def ERR_NOSUCHNICK(self, nickname):
        self.reply("401 %s :No such nick/channel" % nickname)

    def ERR_NOSUCHCHANNEL(self, channel):
        self.reply("403 %s :No such channel" % channel)

    def ERR_NOORIGIN(self):
        self.reply("409 :No origin specified")

    def ERR_UNKNOWNCOMMAND(self, command):
        self.reply("421 %s :Unknown command" % command)

    def ERR_NONICKNAMEGIVEN():
        self.reply("431 :No nickname given")

    def ERR_ERRONEUSNICKNAME(self, nickname):
        self.reply("432 %s :Erroneus nickname" % nickname)

    def ERR_NICKNAMEINUSE(self, nickname):
        self.reply("433 %s :Nickname is already in use" % nickname)

    def ERR_USERNOTINCHANNEL(self, nickname, channel):
        self.reply("441 %s %s :They aren't on that channel" % (nickname, channel))

    def ERR_NEEDMOREPARAMS(self, command):
        self.reply("461 %s :Not enough parameters" % command)

    #Command responses:
    #RPL_TOPIC, etc
    return

class Server(object):
    def __init__(self):
        self.servername = 'IRC SERVER'
        self.channels = {}
        self.clients = {}
        self.nicknames = {} #dictionary keys = nickname & values = client

    def getClient(self, nickname):
        return self.nicknames.get(nickname)


    def start(self):
        HEADER_LENGTH = 10

        IP = "127.0.0.1"
        PORT = 6667

        # Create a socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #allow re-conect
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind, so server informs operating system that it's going to use given IP and port
        server_socket.bind((IP, PORT))

        # This makes server listen to new connections
        server_socket.listen()
        print("Listening for connections on "+IP+" ,Port: "+PORT+"")

        # List of sockets for select.select()
        sockets_list = [server_socket]

        While True:
            read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list) #not 100% sure what this does
            # Iterate over notified sockets
            for notified_socket in read_sockets:

                # If notified socket is a server socket - new connection, accept it
                if notified_socket == server_socket:
                    # Accept new connection
                    client_socket, client_address = server_socket.accept()
                    # Client should send his name right away, receive it
                    user = receive_message(client_socket)
                    sockets_list.append(client_socket)
                    self.clients[client_socket] = user
                    print("Accepted new connection")
                #known connection
                else:
                    message = receive_message(notified_socket)
                    user = clients[notified_socket]
                    print("Received message from "+user["data"].decode("utf-8")+" : "+message["data"].decode("utf-8")+""")

                    for client_socket in clients:
                        client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    def receive_message(client_socket):
        try:
            # Receive our "header" containing message length, it's size is defined and constant
            message_header = client_socket.recv(HEADER_LENGTH)

            # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if len(message_header) < 1:
                return False

            # Convert header to int value
            message_length = int(message_header.decode('utf-8')

            # Return an object of message header and message data
            return {'header': message_header, 'data': client_socket.recv(message_length)}

        except:
            # client closed connection
            return False
    return

class Channel(object):
    def __init__(self, name):
        self.name = name
        self.members = {}
        self._topic = ""
        #add people
        #remove people
    return

def main(arg):
    server = Server()
    return
