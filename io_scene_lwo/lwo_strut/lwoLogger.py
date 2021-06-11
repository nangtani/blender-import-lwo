import sys
import logging

class LWOLogger:
    def __new__(self, type, loglevel=logging.INFO):
        l = logging.getLogger(type)
        l.setLevel(loglevel)

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(loglevel)
        formatter = logging.Formatter("%(levelname)7s: %(name)5s - %(message)s")
        stdout_handler.setFormatter(formatter)

        handler_present = False
        for handler in l.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler_present = True

        if not handler_present:
            l.addHandler(stdout_handler)
        return l
