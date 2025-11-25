import subprocess, threading

class EncoderWorker(threading.Thread):
    def __init__(self, cmd, callback=None):
        super().__init__()
        self.cmd = cmd
        self.callback = callback

    def run(self):
        subprocess.run(self.cmd)
        if self.callback:
            self.callback()
