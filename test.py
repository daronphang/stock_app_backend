import inspect
from datetime import datetime


class TestMixin:
    def get_class_attr(self):
        return str(inspect.signature(self.__class__))

    def get_attr_values(self, instance):
        attributes = str(inspect.signature(self.__class__))
        attr_list = attributes[1:-1].split(', ')
        print(attr_list)
        values_tuple = tuple(map(lambda x: getattr(instance, x), attr_list))
        return values_tuple


class Test(TestMixin):
    def __init__(self, name, value, datetime):
        self.name = name
        self.value = value
        self.datetime = datetime


test = Test('hello', 'world', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

print(test.get_class_attr())
# print(getattr(test, 'name'))
# print(inspect.getmembers(test))
print(test.get_attr_values(test))