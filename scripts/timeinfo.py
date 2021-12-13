from time import sleep, time
from datetime import datetime
from threading import Thread, Lock
from abc import abstractmethod

class TimeInfo:

    stopped = True
    lock = None

    def __init__(self) -> None:
        self.lock = Lock()

    def start(self):
        print('starting time')
        self.stopped = False
        t = Thread(target= self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            print(str(datetime.fromtimestamp(time()))[11:16])
            sleep(60)

    @abstractmethod
    def countdown(seconds):
        while seconds > 0:
            print(seconds)
            sleep(1)
            seconds -= 1
        
        print('go')