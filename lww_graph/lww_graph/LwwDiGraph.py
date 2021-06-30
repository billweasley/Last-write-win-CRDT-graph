from typing import List, Set

from lww_graph.lww_graph.edge.LwwEdge import LwwEdge
from lww_graph.lww_graph.edge.LwwEdgeSet import LwwEdgeSet
from lww_graph.lww_graph.edge.LwwTimedEdge import LwwTimedEdge
from lww_graph.lww_graph.vertex.LwwTimedVertex import LwwTimedVertex
from lww_graph.lww_graph.vertex.LwwVertexSet import LwwVertexSet


class LwwDiGraph(object):
    """
    A Last-Writer-Win state based directed graph implementation.
    """

    def __init__(self):
        # Lww-set for keeping vertex
        self.__v_set__ = LwwVertexSet()

        # Lww-set for keeping edge,
        # Note that you need construct a vertex set before initialising a edge set
        self.__e_set__ = LwwEdgeSet(self.__v_set__)

    def add_vertex(self, vertex: LwwTimedVertex) -> 'LwwDiGraph':
        """
        Add a vertex with timestamp to the graph.

        :param vertex: A LwwTimedVertex object, containing the vertex and timestamp information.
        :return: The graph it self.
        """
        self.__v_set__.add(vertex)
        return self

    def add_edge(self, edge: LwwTimedEdge) -> 'LwwDiGraph':
        """
        Add a edge with timestamp to the graph.

        Note: Here we do not check if an edge is valid when it is added - they can be invalid.
        A valid edge requires its 2 vertices (source and target) existing in vertex set.
        Tombstone mechanism will list only valid edges for a local view.
        (See LwwEdgeSet.exist method for more information).

        By allowing to add (locally and currently) invalid edges and tombstone mechanism,
        it can achieve "eventual consistency" for the case,
        where a happens-before add_vertex operation for this edge arrives later than add_edge (after merge operation).

        :param edge: A LwwTimedVertex object, containing the vertex and timestamp information.
        :return: The graph it self.
        """
        self.__e_set__.add(edge)
        return self

    def remove_vertex(self, vertex: LwwTimedVertex) -> 'LwwDiGraph':
        """
        Remove a vertex from current graph.

        It will do a cascading removal for all edges, where the edges has the target vertex as its source
        or target vertex. It will update remove mark if the vertex is not "currently" found in the local
        copy - in case if later on if a happens-before vertex add operation arrives later (by merge).

        :param vertex: A LwwTimedVertex object, containing the vertex and timestamp information.
        :return: The graph itself.
        """
        vertex_id = vertex.value
        if self.vertex_exist(vertex_id):
            for edge in self.__e_set__.elements():
                if edge.contains(vertex_id):
                    self.remove_edge(LwwTimedEdge(edge, vertex.create_timestamp))

        self.__v_set__.remove(vertex)
        return self

    def remove_edge(self, edge: LwwTimedEdge) -> 'LwwDiGraph':
        """
        Remove an edge from current graph.

        :param edge: A LwwTimedEdge object, containing the edge and timestamp information.
        :return: The graph itself.
        """
        self.__e_set__.remove(edge)
        return self

    def vertex_count(self) -> int:
        """
        Number of vertex in the graph.

        :return: An integer, representing the number of vertex in the graph.
        """
        return self.__v_set__.size()

    def edge_count(self) -> int:
        """
        Number of (valid) edge in the graph.

        :return: An integer, representing the number of (valid) edge in the graph.
        """
        return self.__e_set__.size()

    def vertex_exist(self, vertex_id: int) -> bool:
        """
        Check if a vertex id exist in the local view of this graph.

        :param vertex_id: an integer, the vertex id that needs to look up.
        :return: True if it finds the vertex id in the local view of the graph, otherwise False.
        """
        return self.__v_set__.exist(vertex_id)

    def edge_exist(self, edge: LwwEdge) -> bool:
        """
        Check if a edge exist in the local view of this graph.

        :param edge: A LwwEdge object, containing edge information, which is the edge that needs to look up
        :return: True if it finds the edge in the local view of the graph, otherwise False.
        """
        return self.__e_set__.exist(edge)

    def connected_vertices(self, vertex_id: int) -> List[int]:
        """
        Return all vertices that a vertex connected. This includes in-bounded and out-bounded connections.
        The order of the returned result is NOT guaranteed.

        :param vertex_id: an integer, the vertex id that needs to look up.
        :return: A list of integer, where each represents the a connected vertex for vertex_id.
        """
        appeared = set()
        ret = []
        for edge in self.__e_set__.elements():
            if edge.contains(vertex_id) and edge.counterparty_vertex(vertex_id) not in appeared:
                counter_party = edge.counterparty_vertex(vertex_id)
                ret.append(counter_party)
                appeared.add(counter_party)
        return ret

    def merge(self, another: 'LwwDiGraph') -> 'LwwDiGraph':
        """
        Merge method with another LwwDiGraph to achieve the goal "Eventual consistency" for this graph.

        :param another: Another LwwDiGraph.
        :return: The graph itself, with updated view from another graph.
        """
        self.__v_set__.merge(another.__v_set__)
        self.__e_set__.merge(another.__e_set__)
        return self

    def list_all_path(self, src: int, target: int) -> List[List[int]]:
        """
        List all path from lww_graph to target.

        Here a distinct path is no loop and self-loop.

        :param src: an integer, the source vertex id that needs to look up.
        :param target: an integer, the target vertex id that needs to look up.
        :return: A list of list of integer. Where each list in the list is a path from lww_graph to target.
        """
        result = []
        if not (self.vertex_exist(src) and self.vertex_exist(target)):
            return result
        self.__list_path__dfs__(src, target, set(), [src], result)
        return result

    def __list_path__dfs__(self, src: int, target: int,
                           visited: Set[int], current: List[int], result: List[List[int]]):
        """
        (Internal method) Deep First Search helper for path finding.

        :param src: an integer, the source vertex id that needs to look up.
        :param target: an integer, the target vertex id that needs to look up.
        :param visited: A mark set to break circled visit.
        :param current: Current path.
        :param result: Final result.
        :return: A list of list of integer. Where each list in the list is a path from lww_graph to target.
        """
        if src == target:
            result.append(current)
        else:
            for out_neighbor in self.__connected_vertices_outgoing__(src):
                if out_neighbor not in visited:
                    visited.add(out_neighbor)
                    self.__list_path__dfs__(out_neighbor, target, visited, current + [out_neighbor], result)
                    visited.remove(out_neighbor)

    def __connected_vertices_outgoing__(self, vertex_id: int) -> List[int]:
        """
        Return all vertices that the vertex is the source. Out-bounded connections only.

        :param vertex_id: an integer, the vertex id that needs to look up.
        :return: a list of int, where each represents the a out-bounded connected vertex for vertex_id.
        """
        return [edge.counterparty_vertex(vertex_id)
                for edge in self.__e_set__.elements() if edge.src == vertex_id]

    def __eq__(self, other):
        return isinstance(other, LwwDiGraph) \
               and self.__e_set__ == other.__e_set__\
               and self.__v_set__ == other.__v_set__
