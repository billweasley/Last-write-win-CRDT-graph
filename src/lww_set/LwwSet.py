from typing import Dict, List, Union
from src.LwwTimedObj import LwwTimedObj


class LwwSet(object):
    """
    A Last-Writer-Win state based set implementation.
    """

    def __init__(self, added_mark: Dict[any, int] = None, remove_mark: Dict[any, int] = None):
        self.__added__ = added_mark if added_mark is not None else {}
        self.__removed__ = remove_mark if remove_mark is not None else {}

    def add(self, obj: LwwTimedObj):
        """
        Add element with current timestamp.

        :param obj: The object to be added into the set.
        :return: None
        """
        self.__add__(obj)

    def remove(self, obj: LwwTimedObj):
        """
        Remove element with current timestamp.

        :param obj: The object to be removed into the set.
        :return: None
        """
        self.__remove__(obj)

    def exist(self, obj: any) -> bool:
        """
        Check if an element is in the set.

        :param obj: The object to exam.
        :return: True if the object is presented in the set, otherwise False.
        """
        has_added = obj in self.__added__

        return has_added and ((obj not in self.__removed__) or (self.__added__[obj] > self.__removed__[obj]))

    def elements(self) -> List[any]:
        """
        Get the elements that added to the list.
        :return: A python list, which contains all added object in the set, ascending ordered by last added timestamp.
        """
        res = [key for key in self.__added__.keys() if self.exist(key)]
        res = sorted(res, key=lambda ele: (self.__added__[ele], ele))  # order: (timestamp, object)
        return res

    def elements_with_time(self) -> List[LwwTimedObj]:
        """
        Get LwwTimedObj that for elements that added to the list. This is allowed to check timestamp information
        for objects.
        :return A python list, which contains LwwTimedObj object(s),
        each has the object itself and it timestamp information for when it was added to the list.
        """
        res = [LwwTimedObj(key, self.__added__[key]) for key in self.__added__.keys() if self.exist(key)]
        return sorted(res, key=lambda ele: (self.__added__[ele], ele))  # order: (timestamp, object)

    def size(self) -> int:
        """
        Get the number of objects added to the set.
        :return: A int value, representing the number of elements in the set.
        """
        return len(self.elements())

    def merge(self, another: 'LwwSet') -> 'LwwSet':
        """
        Merge another set to current set.
        :param another: A lww_set.LwwSet.LwwSet to be merged.
        :return: The set it self.
        """
        for obj in another.__added__:
            self.add(LwwTimedObj(obj, another.__added__[obj]))
        for obj in another.__removed__:
            self.remove(LwwTimedObj(obj, another.__removed__[obj]))

        return self

    def last_removed_timestamp(self, obj: any) -> Union[float, int]:
        """
        Get last timestamp for an obj that marks removed. If this obj is not found in the set then return -inf
        :param obj: The object that is looked up.
        :return: The last timestamp the item marked as removed. If the item is not found in deletion set,
        a float type -inf.
        """
        if isinstance(obj, LwwTimedObj):
            obj = obj.value
        return self.__removed__[obj] if obj in self.__removed__ else float('-inf')

    def last_added_timestamp(self, obj: any) -> Union[float, int]:
        """
        Get last timestamp for an obj that marks added. If this obj is not found in the set then return -inf
        :param obj: The object that is looked up.
        :return: The last timestamp the item marked as added. If the item is not found in deletion set,
        a float type -inf.
        """
        if isinstance(obj, LwwTimedObj):
            obj = obj.value
        return self.__added__[obj] if obj in self.__added__ else float('-inf')

    @staticmethod
    def merge_set(set_a: 'LwwSet',
                  set_b: 'LwwSet') -> 'LwwSet':
        """
        Static helper method for merging 2 LwwSet and create new one.
        :param set_a: A lww_set.LwwSet.LwwSet to be merged.
        :param set_b: Another lww_set.LwwSet.LwwSet to be merged.
        :return: A newly created lww_set.LwwSet.LwwSet that contains elements in set_a and set_b
        """
        new_set = LwwSet()
        new_set.merge(set_a)
        new_set.merge(set_b)
        return new_set

    def __eq__(self, other):
        if not isinstance(other, LwwSet):
            return False
        if self.size() != other.size():
            return False
        self_elements = self.elements()
        other_elements = other.elements()
        return all([self_elements[idx] == other_elements[idx] for idx in range(len(self_elements))])

    def __add__(self, obj: LwwTimedObj):
        """
        [internal method] Atomically add an element to the set with a timestamp given.

        :param obj: The LwwTimedObj object to be added into the set.
        :return: None
        """
        self.__mark__(self.__added__, obj.value, obj.create_timestamp)

    def __remove__(self, obj: LwwTimedObj):
        """
        [internal method] Atomically remove an element to the set with a timestamp given.

        :param obj: The LwwTimedObj object to be removed into the set.
        :return: None
        """
        self.__mark__(self.__removed__, obj.value, obj.create_timestamp)

    @staticmethod
    def __mark__(dict_to_add: dict, obj: any, timestamp: int):
        """
        [internal method] The mark process an object in the set. This is required by add() and remove
        operations.

        :param dict_to_add: either self.__added__ dict or self.__removed__ dict
        :param obj: The object to be added.
        :param timestamp: An integer that representing the timestamp that the method is invoked.
        :return: None
        """
        if obj in dict_to_add:
            current_timestamp = dict_to_add[obj]
            if current_timestamp < timestamp:
                dict_to_add[obj] = timestamp
        else:
            dict_to_add[obj] = timestamp
