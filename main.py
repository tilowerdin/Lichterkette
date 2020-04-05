import RPi.GPIO as GPIO
import time
import socket
import threading

_PORT = 2345

CHANGECV = threading.Condition()
CHANGED = list()
VALUES = {
    "close" : False,
    23 : False
}

def initGPIO():
    print(f"setmode to BCM and setup GPIO 23 to OUT")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(23, GPIO.OUT)

def cleanupGPIO():
    print(f"cleanup GPIO")
    GPIO.cleanup()

def on(pin):
    GPIO.output(pin, GPIO.HIGH)

def off(pin):
    GPIO.output(pin, GPIO.LOW)

def toggle(pin, value):
    if value:
        on(pin)
    else:
        off(pin)

class MyThread(threading.Thread):

    def run(self):
        global CHANGED, CHANGECV, VALUES
        while True:
            myList = []
            with CHANGECV:
                while len(CHANGED) == 0:
                    CHANGECV.wait()
                myList = CHANGED
                CHANGED = []

            if "close" in myList:
                break

            for pin in myList:
                toggle(pin, VALUES[pin])

def setValue(key, value):
    global CHANGED, CHANGECV, VALUES
    with CHANGECV:
        VALUES[key] = value
        CHANGED.append(key)
        CHANGECV.notify()
    


if __name__ == '__main__':
    initGPIO()
    try: 
        print("start workerThread")
        workerThread = MyThread()
        workerThread.start()

        
        # create an INET, STREAMing socket
        print("create socket")
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to a public host, and a well-known port
        print(f"bind socket to port {_PORT}")
        serversocket.bind((socket.gethostname(), _PORT))
        # become a server socket
        print("listen to socket")
        serversocket.listen(5)

        while True:
            # accept one connection from outside
            print("accept connections")
            (clientsocket, address) = serversocket.accept()
            # now do something with the clientsocket
            # in this case, we'll pretend this is a threaded server
            print(f"got a connection {address}")

            print("trying to receive message")
            msg = clientsocket.recv(2048).decode()
            print(f"got message: {msg}")

            print("trying to send message")
            clientsocket.send("got your message".encode())

            print("close connection to client")
            clientsocket.close()

            print("set value")
            if msg == "close":
                setValue("close", True)
                workerThread.join()
                break

            setValue(23, not VALUES[23])

    finally:
        setValue("close", True)
        workerThread.join()

        print(f"cleaning up")
        serversocket.close()

        cleanupGPIO()

