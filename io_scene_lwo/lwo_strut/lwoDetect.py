import logging
import struct
from .LWO1 import LWO1
from .LWO2 import LWO2
from .LWO3 import LWO3
from .lwoExceptions import lwoUnsupportedFileException


class LWODetect:
    def __new__(self, filename, loglevel=logging.INFO):
        f = open(filename, "rb")
        try:
            header, chunk_size, chunk_name = struct.unpack(">4s1L4s", f.read(12))
        except:
            f.close()
            raise Exception(f"Error parsing file header! Filename {filename}")
        f.close()
        del f

        if chunk_name == b"LWO2":
            lwo = LWO2(filename, loglevel)
        elif chunk_name == b"LWOB" or chunk_name == b"LWLO":
            # LWOB and LWLO are the old format, LWLO is a layered object.
            lwo = LWO1(filename, loglevel)
        else:
            msg = f"Invalid LWO File Type: {filename}"
            raise lwoUnsupportedFileException(msg)

        return lwo
