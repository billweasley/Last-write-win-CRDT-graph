from typing import Dict

from src.lww_set.LwwSet import LwwSet


class LwwVertexSet(LwwSet):
    """
    Vertex set class for save vertices in LwwDiGraph.
    Its a LwwSet limiting the type of input to integer - for better typing control.
    """
    def __init__(self, added_mark: Dict[int, int] = None,
                 remove_mark: Dict[int, int] = None):
        LwwSet.__init__(self, added_mark, remove_mark)
