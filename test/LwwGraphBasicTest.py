import unittest

from lww_graph.lww_graph.LwwDiGraph import LwwDiGraph
from lww_graph.lww_graph.edge.LwwTimedEdge import LwwTimedEdge
from lww_graph.lww_graph.vertex.LwwTimedVertex import LwwTimedVertex


class LwwGraphBasicTest(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        self.graph = None
        self.graph_1 = None
        self.graph_2 = None
        self.graph_3 = None
        self.graph_A = None
        self.graph_B = None
        self.sorted_neighbors_for_vertex_2 = None

    def test_add_vertex(self):
        self.given_a_empty_lww_di_graph()
        self.when_add_a_vertex_for_empty_graph()
        self.then_graph_has_1_vertex()

    def test_remove_vertex_happens_before_adding_vertex(self):
        self.given_a_di_graph_with_vertex_1_at_time_0()
        self.when_remove_a_vertex_at_time(timestamp=-1)
        self.then_graph_has_1_vertex()

    def test_remove_vertex_happens_concurrently_with_adding_vertex(self):
        self.given_a_di_graph_with_vertex_1_at_time_0()
        self.when_remove_a_vertex_at_time(timestamp=0)
        self.then_graph_has_no_vertex()

    def test_remove_vertex_happens_after_adding_vertex(self):
        self.given_a_di_graph_with_vertex_1_at_time_0()
        self.when_remove_a_vertex_at_time(timestamp=1)
        self.then_graph_has_no_vertex()

    def test_remove_vertex_happens_concurrently_with_adding_edge_containing_the_vertex(self):
        self.given_a_di_graph_with_vertex_1_at_time_0()
        self.when_add_vertex_0_at(timestamp=0)
        self.when_add_an_edge_0_to_1_at_time(timestamp=1)
        self.then_graph_has_1_edge()
        self.when_remove_a_vertex_at_time(timestamp=1)
        self.then_graph_has_no_edge()

    def test_remove_vertex_when_vertex_not_existing(self):
        self.given_a_di_graph_with_vertex_1_at_time_0()
        self.when_remove_a_vertex_2_at_time(timestamp=1)
        self.then_graph_has_1_vertex()

    def test_add_edge_when_no_vertex_existing(self):
        self.given_a_empty_lww_di_graph()
        self.when_add_an_edge_0_to_1_at_time(timestamp=0)
        self.then_graph_has_no_edge()

    def test_add_edge_for_self_loop(self):
        self.given_a_di_graph_with_vertex_1_at_time_0()
        self.when_add_an_edge_1_to_1_at_time(timestamp=1)
        self.then_an_assertion_exception_will_be_thrown()

    def test_add_edge_when_its_vertices_existing(self):
        self.given_a_empty_lww_di_graph()
        self.when_add_vertex_0_at(timestamp=0)
        self.when_add_vertex_1_at(timestamp=0)
        self.when_add_an_edge_0_to_1_at_time(timestamp=1)
        self.then_graph_has_1_edge()

    def test_add_edge_when_its_happens_before_vertices_adding_arrival_later(self):
        self.given_a_empty_lww_di_graph()
        self.when_add_vertex_0_at(timestamp=0)
        self.when_add_an_edge_0_to_1_at_time(timestamp=1)
        self.then_graph_has_no_edge()

        self.when_add_vertex_1_at(timestamp=0)
        self.then_graph_has_1_edge()

    def test_add_edge_when_its_happens_after_vertices_adding_arrival_later(self):
        self.given_a_empty_lww_di_graph()
        self.when_add_vertex_0_at(timestamp=0)
        self.when_add_an_edge_0_to_1_at_time(timestamp=1)
        self.then_graph_has_no_edge()

        self.when_add_vertex_1_at(timestamp=2)
        self.then_graph_has_no_edge()

    def test_remove_edge_does_not_exist(self):
        self.given_a_empty_lww_di_graph()
        self.when_add_vertex_0_at(timestamp=0)
        self.when_add_vertex_1_at(timestamp=0)
        self.when_add_an_edge_0_to_1_at_time(timestamp=1)
        self.when_remove_edge_1_to_2_at_time(timestamp=2)
        self.then_graph_has_1_edge()

    def test_vertex_existing(self):
        self.given_a_di_graph_with_vertex_1_at_time_0()
        self.when_check_if_vertex_existing()
        self.then_vertex_existing_return_true_for(1)
        self.then_vertex_existing_return_false_for(2)

    def test_vertices_connected_to_a_vertex(self):
        self.given_a_connected_di_graph()
        self.when_check_the_neighbors_for_vertex_2()
        self.then_the_neighbors_for_vertex_2_sorted_is_as_expected()

    def test_all_path_between_vertices(self):
        self.given_a_connected_di_graph()
        self.when_check_all_path_from_1_to_6()
        self.then_the_path_found_between_1_and_6_are_as_expected()

    def test_merge_commutativity(self):
        self.given_2_same_graph()
        self.when_graph_1_remove_edge_1_to_2_at_time_4()
        self.when_graph_1_merge_graph_2_with_different_order()
        self.then_merged_graph_are_correct_and_same()

    def test_merge_associativity(self):
        self.given_3_same_graph()
        self.when_graph_1_remove_edge_1_to_2_at_time_4()
        self.when_3_graph_merge_with_different_order()
        self.then_merged_graph_are_correct_and_same()

    def test_merge_idempotence(self):
        self.given_2_same_graph()
        self.when_graph_2_merge_to_itself()
        self.then_graph_1_and_2_are_same()

    def given_a_empty_lww_di_graph(self):
        self.graph = LwwDiGraph()

    def given_a_di_graph_with_vertex_1_at_time_0(self):
        self.graph = LwwDiGraph()
        self.graph.add_vertex(LwwTimedVertex(1, timestamp=0))

    def given_a_connected_di_graph(self):
        """
    The graph looks like the following, * represents an arrow.
                ----
              |     |
              *     |
         1 -* 2 - * 4 - * 5 -* 6
         |    *     |          *
         |    |     |          |
         | -* 3     -----------

        """
        self.graph = LwwDiGraph() \
            .add_vertex(LwwTimedVertex(1, timestamp=1)) \
            .add_vertex(LwwTimedVertex(2, timestamp=1)) \
            .add_vertex(LwwTimedVertex(3, timestamp=1)) \
            .add_vertex(LwwTimedVertex(4, timestamp=1)) \
            .add_vertex(LwwTimedVertex(5, timestamp=1)) \
            .add_vertex(LwwTimedVertex(6, timestamp=1)) \
            .add_edge(LwwTimedEdge((1, 2), timestamp=3)) \
            .add_edge(LwwTimedEdge((1, 3), timestamp=3)) \
            .add_edge(LwwTimedEdge((3, 2), timestamp=3)) \
            .add_edge(LwwTimedEdge((2, 4), timestamp=3)) \
            .add_edge(LwwTimedEdge((4, 2), timestamp=3)) \
            .add_edge(LwwTimedEdge((4, 5), timestamp=3)) \
            .add_edge(LwwTimedEdge((5, 6), timestamp=3)) \
            .add_edge(LwwTimedEdge((4, 6), timestamp=3))

    def given_2_same_graph(self):
        self.graph_1 = LwwDiGraph() \
            .add_vertex(LwwTimedVertex(1, timestamp=1)) \
            .add_vertex(LwwTimedVertex(2, timestamp=1)) \
            .add_edge(LwwTimedEdge((1, 2), timestamp=3))

        self.graph_2 = LwwDiGraph() \
            .add_vertex(LwwTimedVertex(1, timestamp=1)) \
            .add_vertex(LwwTimedVertex(2, timestamp=1)) \
            .add_edge(LwwTimedEdge((1, 2), timestamp=3))

    def given_3_same_graph(self):
        self.graph_1 = LwwDiGraph() \
            .add_vertex(LwwTimedVertex(1, timestamp=1)) \
            .add_vertex(LwwTimedVertex(2, timestamp=1)) \
            .add_edge(LwwTimedEdge((1, 2), timestamp=3))

        self.graph_2 = LwwDiGraph() \
            .add_vertex(LwwTimedVertex(1, timestamp=1)) \
            .add_vertex(LwwTimedVertex(2, timestamp=1)) \
            .add_edge(LwwTimedEdge((1, 2), timestamp=3))

        self.graph_3 = LwwDiGraph() \
            .add_vertex(LwwTimedVertex(1, timestamp=1)) \
            .add_vertex(LwwTimedVertex(2, timestamp=1)) \
            .add_edge(LwwTimedEdge((1, 2), timestamp=3))

    def when_add_a_vertex_for_empty_graph(self):
        self.graph.add_vertex(LwwTimedVertex(1, timestamp=0))

    def when_remove_a_vertex_at_time(self, timestamp):
        self.graph.remove_vertex(LwwTimedVertex(1, timestamp=timestamp))

    def when_remove_a_vertex_2_at_time(self, timestamp):
        self.graph.remove_vertex(LwwTimedVertex(2, timestamp=timestamp))

    def when_add_vertex_0_at(self, timestamp):
        self.graph.add_vertex(LwwTimedVertex(0, timestamp=timestamp))

    def when_add_vertex_1_at(self, timestamp):
        self.graph.add_vertex(LwwTimedVertex(1, timestamp=timestamp))

    def when_check_if_vertex_existing(self):
        # empty method for readability
        pass

    def when_add_an_edge_1_to_1_at_time(self, timestamp):
        with self.assertRaises(AssertionError):
            self.graph.add_edge(LwwTimedEdge((1, 1), timestamp))

    def when_add_an_edge_0_to_1_at_time(self, timestamp):
        self.graph.add_edge(LwwTimedEdge((0, 1), timestamp))

    def when_remove_an_edge_0_to_1_at_time(self, timestamp):
        self.graph.remove_edge(LwwTimedEdge((0, 1), timestamp))

    def when_remove_edge_1_to_2_at_time(self, timestamp):
        self.graph.remove_edge(LwwTimedEdge((1, 2), timestamp))

    def when_graph_1_remove_edge_1_to_2_at_time_4(self):
        self.graph_1.remove_edge(LwwTimedEdge((1, 2), timestamp=4))

    def when_graph_1_merge_graph_2_with_different_order(self):
        self.graph_A = self.graph_1.merge(self.graph_2)
        self.graph_B = self.graph_2.merge(self.graph_1)

    def when_3_graph_merge_with_different_order(self):
        self.graph_A = self.graph_1.merge(self.graph_2).merge(self.graph_3)
        self.graph_B = self.graph_3.merge(self.graph_2).merge(self.graph_1)

    def when_graph_2_merge_to_itself(self):
        self.graph_2 = self.graph_2.merge(self.graph_2)

    def when_check_the_neighbors_for_vertex_2(self):
        self.sorted_neighbors_for_vertex_2 = [1, 3, 4]

    def when_check_all_path_from_1_to_6(self):
        self.sorted_path_from_1_to_6_set = {"1->2->4->5->6", "1->3->2->4->5->6", "1->2->4->6", "1->3->2->4->6"}

    def then_an_assertion_exception_will_be_thrown(self):
        # empty method for readability
        pass

    def then_graph_has_1_vertex(self):
        self.assertEqual(self.graph.vertex_count(), 1)

    def then_graph_has_no_vertex(self):
        self.assertEqual(self.graph.vertex_count(), 0)

    def then_graph_has_vertices_of(self, n):
        self.assertEqual(self.graph.vertex_count(), n)

    def then_graph_has_1_edge(self):
        self.assertEqual(self.graph.edge_count(), 1)

    def then_graph_has_no_edge(self):
        self.assertEqual(self.graph.edge_count(), 0)

    def then_graph_has_edges_of(self, num):
        self.assertEqual(self.graph.edge_count(), num)

    def then_vertex_existing_return_true_for(self, vertex_id):
        self.assertEqual(self.graph.vertex_exist(vertex_id), True)

    def then_vertex_existing_return_false_for(self, vertex_id):
        self.assertEqual(self.graph.vertex_exist(vertex_id), False)

    def then_the_neighbors_for_vertex_2_sorted_is_as_expected(self):
        self.assertListEqual(sorted(self.graph.connected_vertices(2)), self.sorted_neighbors_for_vertex_2)

    def then_the_path_found_between_1_and_6_are_as_expected(self):
        founded_path = ["->".join([str(i) for i in p]) for p in self.graph.list_all_path(1, 6)]
        self.assertEqual(len(founded_path), len(self.sorted_path_from_1_to_6_set))
        self.assertEqual(set(founded_path) - self.sorted_path_from_1_to_6_set, set())

    def then_merged_graph_are_correct_and_same(self):
        self.assertEqual(self.graph_A.edge_count(), 0)
        self.assertEqual(self.graph_A, self.graph_B)

    def then_graph_1_and_2_are_same(self):
        self.assertEqual(self.graph_1, self.graph_2)


if __name__ == '__main__':
    unittest.main()
