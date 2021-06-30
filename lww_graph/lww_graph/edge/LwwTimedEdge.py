from typing import Union, Tuple

from lww_graph.LwwTimedObj import LwwTimedObj
from lww_graph.lww_graph.edge.LwwEdge import LwwEdge


class LwwTimedEdge(LwwTimedObj):
    """
    Edge with timestamp information.
    Its a LwwTimedObj object limiting the type of input to either a LwwEdge or a Tuple - for better typing control.
    """
    def __init__(self, edge: Union[LwwEdge, Tuple], timestamp: int = None):
        if isinstance(edge, Tuple):
            edge = LwwEdge(edge[0], edge[1])
        LwwTimedObj.__init__(self, edge, timestamp)

