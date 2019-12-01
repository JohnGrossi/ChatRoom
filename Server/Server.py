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
    def __init__(self, server, socket):
        self.server = server
        self.socket = socket
        self.realName = None
        self.nickname = None
        self.writeBuffer = ""
        self.rec_buffer = ""
        self.nick = ""
        self.name = ""
        self.user = ""
        self.registered = False
        self.line_regex = re.compile(r"\r?\n")
        #etc
<<<<<<< HEAD

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

            #look at
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

        def list():
            print("list")

        def privmsg():
            print("privmsg")

        #def notice():

        def ping():
            print("ping")

        def pong():
            print("pong")

        #look at
        def ping(self, arguments):
            if len(arguments) == 0:
                ERR_NOORIGIN()
            else:
                self.reply("PONG %s" % arguments[0])

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
=======


    def join(self, arguments):
        return
    def part(self, arguments):
        return

def ping(self, arguments):
    if len(arguments) == 0:
        ERR_NOORIGIN()
    else:
        self.reply("PONG %s" % arguments[0])

def ping(self, arguments):
    if len(arguments) == 0:
        ERR_NOORIGIN()
    else:
        self.reply("PONG %s" % arguments[0])

    def listHandler(self, arguments):
        return

    def privmsg(self, arguments):
        return

    #def notice(self, arguments):



    def pong(self, arguments):
        pass

    def wallops(self, arguments):
        return

    def who(self, arguments):
        return

    def topic(self, arguments):
        return



    def commandHandler(self, command, arguments):
        commands = {
        "JOIN" : join,
        "PART" : part,
        "NICK" : nick,
        "LIST" : listHandler,
>>>>>>> c4818e472f95aa48cdfa1e31792a445ad38aed2e
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
            self.ERR_UNKNOWNCOMMAND()

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


    def disconnect(self, message):
        self.reply("QUIT :%s" % message)
        #remove client & close socket

    def message(self, message):
        #self.writeBuffer += message + "\r\n"
        self.socket.send((message + "\r\n").encode())
        print(message)

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

    def __init__(self):
        self.channels = {}
        self.clients = {}
        self.nicknames = {}
        self.port = 6667
        self.ip = "127.0.0.1"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rec_buffer = ""
        self.line_regex = re.compile(r"\r?\n")

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


client = Client("","")
client.get_connection()
while True:
    client.socket_readable()
    if(not client.buffer_empty()):
        client.parse_buffer()

def main():
    server = Server()
    server.run()

if __name__ == "__main__":
    main()
