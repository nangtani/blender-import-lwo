BPY_DEBUG = 1

class DebugException:
    def __init__(self, msg, debug=BPY_DEBUG):
        
        if 0 == BPY_DEBUG:
            return
        if 1 == debug:
            print(msg)
        elif 2 == debug:
            raise Exception(msg)
