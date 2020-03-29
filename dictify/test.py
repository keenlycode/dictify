import unittest
import json
import uuid
from dictify import Model, Field, FieldError, ModelError


class User(Model):
    name = Field().type(str)
    email = Field().type(str)


class MockUp(Model):

    def uuid4_rule(field):
        try:
            id_ = uuid.UUID(field.value)
        except AttributeError:
            raise AttributeError(f"Can't parse value to UUID")
        assert id_.version == 4, f"Value is UUID v{id_.version}, not v4"

    default = Field(default='default')
    required = Field(required=True)
    anyof = Field().anyof([1, 2, 3])
    verify = Field(default=str(uuid.uuid4())).verify(uuid4_rule)
    length = Field().length(min=2, max=10)
    listof = Field().listof(str)
    match = Field().search('[0-9]+')
    min = Field().min(0)
    max = Field().max(10)
    subset = Field().subset([1, 2, 3])
    type = Field().type(str)
    

# class TestModel(unittest.TestCase):

#     def setUp(self):
#         self.model = User({'name': 'initial name'})

#     def test_data_unmodified(self):
#         data = {'name': 'test'}
#         User(data)
#         self.assertDictEqual(data, {'name': 'test'})

#     def test_setitem(self):
#         """Test `__setitem__` for 3 cases:
#         Key Error, ValueError and Success.
#         """
#         data = self.model.copy()
#         with self.assertRaises(FieldError):
#             self.model['name'] = 0
#         with self.assertRaises(KeyError):
#             self.model['age'] = 20
#         self.assertDictEqual(
#             data, self.model,
#             f"Model's data is the same after error")
#         self.assertEqual(self.model['name'], 'initial name')
#         self.model['name'] = 'new name'
#         self.assertEqual(self.model['name'], 'new name')

#     def test_update(self):
#         """Test `update` to raise KeyError and ValueError as Exception."""
#         data = self.model.copy()
#         with self.assertRaises(ModelError):
#             self.model.update({'a': 1})
#         with self.assertRaises(ModelError):
#             self.model.update({'name': 1})
#         self.assertDictEqual(
#             data, self.model,
#             f"Model's data is the same after error")
        

class TestField(unittest.TestCase):

    def setUp(self):
        self.model = MockUp({'required': True})

    def test_anyof(self):
        self.model['anyof'] = 1
        with self.assertRaises(FieldError):
            self.model['anyof'] = 5

    def test_verify(self):
        self.model['verify'] = '11fadebb-3c70-47a9-a3f0-ebf2a3815993'

    def test_default(self):
        self.assertEqual(self.model['default'], 'default')

#     def test_length(self):
#         self.model['length'] = 'hello'
#         with self.assertRaises(ValueError):
#             self.model['length'] = 'test-with-lenght-more-than-10'

#     def test_listof(self):
#         list_of_string = ['ab', 'cd']
#         self.model['listof'] = list_of_string
#         with self.assertRaises(ValueError):
#             self.model['listof'] = [1, 2]
#             self.assertEqual(self.model['listof'], list_of_string)

#     def test_match(self):
#         self.model['match'] = '0123456789'
#         match = self.model['match']
#         with self.assertRaises(ValueError):
#             self.model['match'] = 'a'
#             self.assertEqual(self.model['match'], match)

#     def test_number(self):
#         self.model['number'] = 1
#         with self.assertRaises(ValueError):
#             self.model['number'] = 21
#             self.assertEqual(self.model['number'], 1)

#     def test_range(self):
#         self.model['range'] = 1
#         with self.assertRaises(ValueError):
#             self.model['range'] = 21
#             self.assertEqual(self.model['range'], 1)

#     def test_required(self):
#         required = self.model['required']
#         with self.assertRaises(ValueError):
#             self.model['required'] = None
#             self.assertEqual(self.model['required'], required)

#     def test_subset(self):
#         self.model['subset'] = [1, 2, 3]

#     def test_type(self):
#         string = 'test'
#         self.model['type'] = string
#         with self.assertRaises(ValueError):
#             self.model['type'] = 1
#             self.assertEqual(self.model['type'], string)

#     def test_json(self):
#         json.dumps(self.model)

# class TestSubClass(unittest.TestCase):
#     def setUp(self):
#         class Content(BaseModel):
#             content_type = Field().type(str)

#         class HTML(Content):
#             pass

#         self.html = HTML()

#     def test_subclass(self):
#         with self.assertRaises(ValueError):
#             self.html['content_type'] = 1


if __name__ == '__main__':
    unittest.main()
