import inspect
from datetime import datetime


class TestMixin:
    class_attr = 1

    def get_class_attr(self):
        return str(inspect.signature(self.__class__))

    def get_attr_values(self, instance):
        attributes = str(inspect.signature(self.__class__))
        attr_list = attributes[1:-1].split(', ')
        print(attr_list)
        values_tuple = tuple(map(lambda x: getattr(instance, x), attr_list))
        return values_tuple
    
    def values(self):
        return list(self.__dict__.values())


class Test(TestMixin):
    def __init__(self, name, value, datetime):
        self.name = name
        self.value = value
        self.datetime = datetime


test = Test('hello', 'world', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

query = {'id': '123'}
query_op = {'AND': {'id': '123'}}
test_set = set(['AND', 'OR'])

print(bool(set(query.keys()).intersection(test_set)))

# if query_op.keys() not in ['AND', 'OR']:
#     print(query_op.keys())
#     print('trueeee')