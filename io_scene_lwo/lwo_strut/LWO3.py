from .lwoBase import LWOBase


class LWO3(LWOBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_types = [b"LWO3"]
