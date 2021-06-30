from typing import Dict, List

from lww_graph.lww_graph.edge.LwwEdge import LwwEdge
from lww_graph.lww_graph.edge.LwwTimedEdge import LwwTimedEdge
from lww_graph.lww_graph.vertex.LwwVertexSet import LwwVertexSet
from lww_graph.lww_set.LwwSet import LwwSet


class LwwEdgeSet(LwwSet):
    """
    Edge set class for save edges in LwwDiGraph.
    Note it requires a LwwVertexSet as input because an edge, e = v x v, in a graph.

    Its a LwwSet limiting the type of input to LwwEdge - for better typing control.
    It also rewrite the exist, elements and elements_with_time methods to implement Tombstone mechanism.
    """

    def __init__(self, node_set: 'LwwVertexSet' = None,
                 added_mark: Dict[LwwEdge, int] = None,
                 remove_mark: Dict[LwwEdge, int] = None):
        LwwSet.__init__(self, added_mark, remove_mark)
        self.node_set = node_set

    def exist(self, edge: LwwEdge) -> bool:
        """
        Check if a (valid) LwwEdge existing in the set.

        This ensures the edge is valid as well. A edge is defined existing and valid only if all of the following
        conditions satisfied:

        Suppose all Timestamp, Ts, below are initialised with -inf.

        - Existence of an edge:
            - itself exist in the graph (Ts_{last_add_edge} > Ts_{last_remove_edge}),

        - Existence of 2 vertices in this edge:
            - its source vertex exist in the graph (Ts_{last_add_source_vertex} > Ts_{last_remove_source_vertex})
            - its target vertex exist in the graph (Ts_{last_add_target_vertex} > Ts_{last_remove_target_vertex})

        - Validity of an edge, given the fact of E: V x V:
            - its source vertex added earlier than the edge itself (Ts_{last_add_edge} > Ts_{last_add_source_vertex})
            - its target vertex added earlier than the edge itself (Ts_{last_add_edge} > Ts_{last_add_target_vertex})

        :param edge: The edge to exam.
        :return: True if the edge is valid and is presented in the set, otherwise False.
        """
        return super().exist(edge) \
               and self.node_set.exist(edge.src) \
               and self.node_set.exist(edge.target) \
               and self.node_set.last_added_timestamp(edge.src) < self.last_added_timestamp(edge) \
               and self.node_set.last_added_timestamp(edge.target) < self.last_added_timestamp(edge)

    def elements(self) -> List[LwwEdge]:
        """
        Get the valid edges that added to the list.
        This overwrite was for better typing control.

        :return: A python list, which contains all added LwwEdge in the set, ascending ordered by last added timestamp.
        """
        return super().elements()

    def elements_with_time(self) -> List[LwwTimedEdge]:
        """
        Get valid edges with timestamp added to the list. This is allowed to check timestamp information
        for edges.
        This overwrite was for better typing control.

        :return A python list, which contains LwwTimedEdge object(s), ascending ordered by last added timestamp.
        """
        res = [LwwTimedEdge(key, self.__added__[key]) for key in self.__added__.keys() if self.exist(key)]
        return sorted(res, key=lambda ele: (self.__added__[ele], ele))  # order: (timestamp, object)

