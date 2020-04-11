import socket
import sys

_PORT = 2345
_MESSAGE_LEN = 4096


def sendToServer(msg):
    global _PORT, _MESSAGE_LEN
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    print("trying to connect")
    # s.connect((socket.gethostname(), _PORT))
    s.connect(('192.168.8.103', _PORT))
    print("connected")

    print("trying to send message")
    s.send(msg.encode())
    print("send message")

    print("trying to receive message")
    msg = s.recv(_MESSAGE_LEN).decode()
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

