import RPi.GPIO as GPIO
import time
import socket
import threading

_PORT = 2345

# Abwechselnd Zeit an, Zeit aus, ...
MUSTER = {
    'on': (1, [(True,-1)]),
    'off': (1, [(False,-1)]),
    'blink': (-1, [(False,1),(True,1)])
}

CHANGECV = {
    23 : threading.Condition()
}
CHANGED = list()
VALUES = {
    23 : (1, [(0, -1)])
}
STOP = False

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

    def __init__(self, lightId):
        threading.Thread.__init__(self)
        self.__id = lightId
        self.__task = MUSTER['off']
        self.__progress = self.__task[1].copy()
        self.__count = self.__task[0]


    def run(self):
        global CHANGECV, VALUES, STOP
        while True:
            with CHANGECV[self.__id]:
                if STOP:
                    break

                if self.__id in CHANGED:
                    CHANGED.remove(self.__id)
                    self.__task = VALUES[self.__id]
                    self.__progress = self.__task[1].copy()
                    self.__count = self.__task[0]

            if self.__count == 0:
                off(self.__id)
                with CHANGECV[self.__id]:
                    while not (self.__id in CHANGED):
                        CHANGECV[self.__id].wait()
            else:
                self.__count = max(-1, self.__count-1)
                if len(self.__progress) == 0:
                    self.__progress = self.__task[1].copy()
                task = self.__progress.pop(0)
                toggle(self.__id, task[0])
                with CHANGECV[self.__id]:
                    if task[1] == -1:
                        CHANGECV[self.__id].wait()
                    else:
                        CHANGECV[self.__id].wait(task[1])

def setValue(key, value):
    global CHANGED, CHANGECV, VALUES
    with CHANGECV[key]:
        VALUES[key] = value
        CHANGED.append(key)
        CHANGECV[key].notifyAll()

def stopAll():
    global STOP
    STOP = True
    for key in CHANGECV:
        with CHANGECV[key]:
            CHANGECV[key].notifyAll()


if __name__ == '__main__':
    initGPIO()

    print("start workerThread")
    pins = [23]
    workerThreads = {}
    for pin in pins:
        workerThreads[pin] = MyThread(pin)
        workerThreads[pin].start()

    try: 
        # create an INET, STREAMing socket
        print("create socket")
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
                stopAll()
                for pin in pins:
                    workerThreads[pin].join()
                break

            if msg == 'on':
                setValue(23, MUSTER['on'])
            elif msg == 'blink':
                setValue(23, MUSTER['blink'])
            else:
                setValue(23, MUSTER['off'])

    finally:
        stopAll()
        for pin in pins:
            workerThreads[pin].join()

        print(f"cleaning up")
        serversocket.close()

        cleanupGPIO()

