from time import sleep, time
from datetime import datetime
from threading import Thread, Lock

class TimeInfo:

    stopped = True
    lock = None

    def __init__(self) -> None:
        self.lock = Lock()

    def start(self):
        print('starte time')
        self.stopped = False
        t = Thread(target= self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            print(str(datetime.fromtimestamp(time()))[11:16])
            sleep(60)