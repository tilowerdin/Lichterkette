import socket
import sys

_PORT = 2345


def sendToServer(msg):
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    
    print("trying to connect")
    # s.connect((socket.gethostname(), _PORT))
    s.connect(('raspberrypi', _PORT))
    print("connected")

    print("trying to send message")
    s.send(msg.encode())
    print("send message")

    print("trying to receive message")
    msg = s.recv(2048).decode()
    print(f"got answer: {msg}")

    print("cleanup")
    s.close()



if __name__ == "__main__":
    args = sys.argv
    print(args)
    if (len(args) > 1):
        sendToServer(args[1])
    else:
        sendToServer("Hallo Welt!")

