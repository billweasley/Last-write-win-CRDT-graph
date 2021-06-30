from src.LwwTimedObj import LwwTimedObj


class LwwTimedVertex(LwwTimedObj):
    """
    Vertex with timestamp information.
    Its a LwwTimedObj object limiting the type of input to integer - for better typing control.
    """
    def __init__(self, vertex_id: int, timestamp: int = None):
        LwwTimedObj.__init__(self, vertex_id, timestamp)
