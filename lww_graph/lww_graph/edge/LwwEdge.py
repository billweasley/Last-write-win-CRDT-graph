class LwwEdge(object):

    def __init__(self, src: int, target: int):
        assert src != target, "You cannot create edge with same lww_graph and target value."
        self.src = src
        self.target = target

    def contains(self, vertex_id: int):
        return self.src == vertex_id or self.target == vertex_id

    def counterparty_vertex(self, vertex_id: int):
        assert self.contains(vertex_id), "Can only find counterparty vertex id for vertex in the edge. "
        return self.src if vertex_id == self.target else self.target

    def __eq__(self, other):
        if not isinstance(other, LwwEdge):
            return False
        return self.src == other.src and self.target == other.target

    def __str__(self):
        return "Edge[{} -> {}]".format(self.src, self.target)

    def __hash__(self):
        return (self.src << 32) + self.target

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        if not isinstance(other, LwwEdge):
            raise ValueError("Cannot compare")
        return self.src - other.src if self.src != other.src else self.target - other.target
