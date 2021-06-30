import time


class LwwTimedObj(object):
    """
    General wrapper for object with timestamp.
    """

    def __init__(self, value: any, timestamp: int = None):
        self.__ensure_printable__(value)
        self.value = value
        self.create_timestamp = time.monotonic_ns() if timestamp is None else timestamp

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "LwwTimedObj[" + self.value.__str__() + "]"

    def __lt__(self, other: 'LwwTimedObj') -> bool:
        self.__ensure_type_LwwObj__(other)
        return self.create_timestamp < other.create_timestamp

    def __le__(self, other: 'LwwTimedObj') -> bool:
        self.__ensure_type_LwwObj__(other)
        return self.create_timestamp <= other.create_timestamp

    def __ge__(self, other: 'LwwTimedObj') -> bool:
        self.__ensure_type_LwwObj__(other)
        return self.create_timestamp >= other.create_timestamp

    def __gt__(self, other: 'LwwTimedObj') -> bool:
        self.__ensure_type_LwwObj__(other)
        return self.create_timestamp > other.create_timestamp

    def __eq__(self, other: any) -> bool:
        if other is None:
            return self.value is None
        if isinstance(other, LwwTimedObj):
            other = other.value
        return isinstance(other, type(self.value)) and other == self.value

    def __ne__(self, other: 'LwwTimedObj') -> bool:
        self.__ensure_type_LwwObj__(other)
        return not self.__eq__(other)

    def __hash__(self):
        return self.value.__hash__() if self.value is not None else 0

    @staticmethod
    def __ensure_printable__(obj):
        try:
            str(obj)
        except NameError as ne:
            raise ValueError("Object has to be printable. Exception: " + str(ne))

    @staticmethod
    def __ensure_type_LwwObj__(obj):
        if not isinstance(obj, LwwTimedObj):
            raise ValueError("The provided object should be a LwwTimedObj, but it has the type of " + str(type(obj)))
