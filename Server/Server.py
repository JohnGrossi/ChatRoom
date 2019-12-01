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
        return
    def part(self, arguments):
        return
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
                print("")
                #change in server dictionary etc
            else:
                ERR_ERRONEUSNICKNAME()
        else:
            ERR_NICKNAMEINUSE()




    def listHandler(self, arguments):
        return

    def privmsg(self, arguments):
        return

    #def notice(self, arguments):

    def ping(self, arguments):
        if len(arguments) == 0:
            ERR_NOORIGIN()
        else:
            self.reply("PONG %s" % arguments[0])

    def pong(self, arguments):
        pass

    def wallops(self, arguments):
        return

    def who(self, arguments):
        return

    def topic(self, arguments):
        return

    def quit(self, arguments):
        if len(arguments) == 0:
            quitMsg = self.nickname
        else:
            quitMsg = arguments[0]
        self.disconnect(quitMsg)

    def commandHandler(self, command, arguments):
        commands = {
        "JOIN" : join,
        "PART" : part,
        "NICK" : nick,
        "LIST" : listHandler,
        "PRIVMSG" : privmsg,
        "NOTICE" : privmsg,
        "PING" : ping,
        "PONG" : pong,
        "WALLOPS" : wallops,
        "WHO" : who,
        "TOPIC" : topic,
        "QUIT" : quit,
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
    #return

class Server(object):
    def run(self):
        ip = "127.0.0.1"
        port = 6667
        # Create a socket, set up, and listening for new connections
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((ip, port))
        server_socket.listen()

        # List of sockets and clients
        sockets_list = [server_socket]
        clients = {}

        print("Listening for connections on: " +ip+" Port: "+str(port)+"")

        while True:
            read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list) #waits for input

            # Iterate over notified sockets
            for notified_socket in read_sockets:

                # If notified socket is a server socket - new connection, accept it
                if notified_socket == server_socket:

                    # Accept new connection
                    client_socket, client_address = server_socket.accept()

                    # Client should send his name right away, receive it
                    user = receive_message(client_socket)

                    # If False - client disconnected before he sent his name
                    if user is False:
                        continue

                    # Add accepted socket to select.select() list
                    sockets_list.append(client_socket)

                    # Also save username and username header
                    clients[client_socket] = user

                    print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

                # Else existing socket is sending a message
                else:

                    # Receive message
                    message = receive_message(notified_socket)

                    # If False, client disconnected, cleanup
                    if message is False:
                        print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                        # Remove from list for socket.socket()
                        sockets_list.remove(notified_socket)

                        # Remove from our list of users
                        del clients[notified_socket]

                        continue

                    # Get user by notified socket, so we will know who sent the message
                    user = clients[notified_socket]

                    print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

                    # Iterate over connected clients and broadcast message
                    for client_socket in clients:

                        # But don't sent it to sender
                        if client_socket != notified_socket:

                            # Send user and message (both with their headers)
                            # We are reusing here message header sent by sender, and saved username header send by user when he connected
                            client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

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
    #return

def main():
    server = Server()
    server.run()

if __name__ == "__main__":
    main()
