import unittest

from src.LwwTimedObj import LwwTimedObj
from src.lww_set.LwwSet import LwwSet


class LwwSetTest(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        self.set = None
        self.set1 = None
        self.set2 = None
        self.set3 = None
        self.setA = None
        self.setB = None

    def test_empty_set_has_no_element(self):
        self.given_an_empty_set()
        self.when_have_an_empty_test()
        self.then_empty_set_has_no_element()

    def test_add_element(self):
        self.given_an_empty_set()
        self.when_add_an_element_to_empty_set()
        self.then_empty_set_has_1_element()

    def test_add_element_duplicated(self):
        self.given_an_empty_set()
        self.when_add_same_element_duplicate()
        self.then_timestamp_for_element_is_newest()

    def test_remove_element(self):
        self.given_a_set_with_element()
        self.when_remove_element()
        self.then_empty_set_has_no_element()

    def test_remove_element_with_older_timestamp(self):
        self.given_a_set_with_element()
        self.when_remove_element_with_older_timestamp()
        self.then_empty_set_has_1_element()

    def test_remove_from_empty_set(self):
        self.given_an_empty_set()
        self.when_remove_element()
        self.then_empty_set_has_no_element()

    def test_order_for_interval_add(self):
        self.given_an_empty_set()
        self.when_add_intermediately()
        self.then_element_order_as_expected_when_added_intermediately()

    def test_same_time_add_and_remove_lead_remove_wins(self):
        self.given_an_empty_set()
        self.when_add_and_remove_happens_same_time()
        self.then_empty_set_has_no_element()

    def test_merge_associativity(self):
        self.given_3_sets_with_distinct_element()
        self.when_merge_3_sets_in_different_order()
        self.then_merged_set_are_same()

    def test_merge_commutativity(self):
        self.given_2_sets_with_distinct_element()
        self.when_merge_2_set_in_different_order()
        self.then_merged_set_are_same()

    def test_merge_idempotence(self):
        self.given_a_set_with_element()
        self.when_merge_with_itself()
        self.then_same_merged_set_are_same()

    def given_an_empty_set(self):
        self.set = LwwSet()

    def given_a_set_with_element(self):
        self.set = LwwSet()
        self.set.add(LwwTimedObj("test", 1))

    def given_2_sets_with_distinct_element(self):
        self.set1 = LwwSet()
        self.set1.add(LwwTimedObj("test-1"))
        self.set2 = LwwSet()
        self.set2.add(LwwTimedObj("test-2"))

    def given_3_sets_with_distinct_element(self):
        self.set1 = LwwSet()
        self.set1.add(LwwTimedObj("test-1"))
        self.set2 = LwwSet()
        self.set2.add(LwwTimedObj("test-2"))
        self.set3 = LwwSet()
        self.set3.add(LwwTimedObj("test-3"))

    def when_have_an_empty_test(self):
        # empty method for readability
        pass

    def when_add_an_element_to_empty_set(self):
        self.set.add(LwwTimedObj("test"))

    def when_add_same_element_duplicate(self):
        self.set.add(LwwTimedObj("test", 2))
        self.set.add(LwwTimedObj("test", 1))

    def when_add_intermediately(self):
        self.set.add(LwwTimedObj("test", 2))
        self.set.add(LwwTimedObj("test-2", 1))
        self.set.add(LwwTimedObj("test", 1))

    def when_remove_element(self):
        self.set.remove(LwwTimedObj("test", 2))

    def when_add_and_remove_happens_same_time(self):
        self.set.add(LwwTimedObj("test", 1))
        self.set.remove(LwwTimedObj("test", 1))
        self.set.add(LwwTimedObj("test", 1))

    def when_remove_element_with_older_timestamp(self):
        self.set.remove(LwwTimedObj("test", 0))

    def when_add_remove(self):
        self.set.add(LwwTimedObj("test", 2))
        self.set.add(LwwTimedObj("test-2", 1))
        self.set.add(LwwTimedObj("test", 1))

    def when_merge_2_set_in_different_order(self):
        self.setA = self.set1.merge(self.set2)
        self.setB = self.set2.merge(self.set1)

    def when_merge_3_sets_in_different_order(self):
        self.setA = self.set1.merge(self.set2).merge(self.set3)
        self.setB = self.set3.merge(self.set2).merge(self.set1)

    def when_merge_with_itself(self):
        self.setA = self.set.merge(self.set)

    def then_empty_set_has_no_element(self):
        self.assertEqual(self.set.size(), 0)

    def then_empty_set_has_1_element(self):
        self.assertEqual(self.set.size(), 1)

    def then_timestamp_for_element_is_newest(self):
        self.assertEqual(self.set.elements_with_time()[0].create_timestamp, 2)

    def then_element_order_as_expected_when_added_intermediately(self):
        self.assertEqual(self.set.elements()[0], 'test-2')
        self.assertEqual(self.set.elements()[1], 'test')

    def then_merged_set_are_same(self):
        self.assertEqual(self.setA, self.setB)

    def then_same_merged_set_are_same(self):
        self.assertEqual(self.set, self.setA)


if __name__ == '__main__':
    unittest.main()
