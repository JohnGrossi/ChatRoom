import socket
import select
import errno
import sys

IP = "127.0.0.1"
PORT = 6667
NICKNAME = "Bot"

if (len(sys.argv) > 1):
    IP = sys.argv[1]
    if(len(sys.argv) > 2):
        NICKNAME = sys.argv[2]

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
client_socket.setblocking(False)

# Prepare username and header and send them
msg = "USER " + NICKNAME + " " + NICKNAME + " " + NICKNAME + " " + NICKNAME + " \r\nNICK " + NICKNAME + "\r\n"
client_socket.send(msg.encode())

rec_buffer = ""


while True:



    try:
        # Now we want to loop over received messages (there might be more than one) and print them
        # while True:

            rec_buffer += client_socket.recv(1000).decode()

            print(rec_buffer)


    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data error is going to be raised
        # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
        # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # We just did not receive anything
        continue





