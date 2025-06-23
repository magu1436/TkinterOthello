
class TkinterOthelloException(Exception):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs