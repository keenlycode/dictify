import unittest
import json
import uuid
from datetime import datetime
from dictify import Model, Field, ModelError


class User(Model):
    id = Field(default=uuid.uuid4()).type(uuid.UUID)
    name = Field(required=True)


class Comment(Model):
    content = Field().type(str)
    datetime = Field(default=datetime.utcnow()).type(datetime)
    user = Field(required=True).type(User)


class Note(Model):
    title = Field(required=True).type(str)
    content = Field().type(str)
    datetime = Field(default=datetime.utcnow()).type(datetime)
    user = Field(required=True).type(User)
    comments = Field().listof(Comment)


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
    length = Field().length(min=2, max=10)
    listof = Field().listof(str)
    min = Field().min(0)
    max = Field().max(10)
    search = Field().search('[0-9]+')
    subset = Field().subset([1, 2, 3])
    type = Field().type(str)
    verify = Field().verify(uuid4_rule)
    

class TestModel(unittest.TestCase):

    def test_init(self):
        # Test when initial data is not type of dict.
        with self.assertRaises(AssertionError):
            Note([])
        
        # Test required field.
        with self.assertRaises(ModelError):
            Note({})

        note = Note({
            'title': 'Title',
            'user': User({'name': 'user example'})
        })

        # Test default value.
        self.assertIsInstance(note['datetime'], datetime)

        # Test successful initial
        data = {
            'title': 'Title',
            'content': 'Content',
            'datetime': datetime.utcnow(),
            'user': User({
                'id': uuid.uuid4(),
                'name': 'user example'
            })
        }
        note = Note(data)
        self.assertDictEqual(note, data)

    def test_setitem(self):
        """Test `__setitem__` for 4 cases:
        1. FieldError,
        2. Key Error
        3. Data unmodified if there is any error.
        4. Success.
        """

        note = Note({
            'title': 'Title',
            'user': User({'name': 'user example'})
        })
        data = note.copy()

        # 1. FieldError.
        with self.assertRaises(ModelError):
            note['title'] = 0

        # 2. KeyError.
        with self.assertRaises(ModelError):
            note['datetime'] = 'today'

        # 3. Data unmodified if there is any error.
        self.assertDictEqual(
            data, note,
            f"Data must be the same if there is any error")

        # 4. Success.
        note['title'] = 'New Title'
        self.assertEqual(note['title'], 'New Title')

    def test_to_dict(self):
        note = Note({
            'title': 'Title',
            'user': User({'name': 'user example'})
        })
        note = note.to_dict()
        # Assert field contains `Model` instance becomes `dict` instance.
        self.assertIs(type(note['user']), dict)
        
    def test_update(self):
        note = Note({
            'title': 'Title',
            'user': User({'name': 'user example'})
        })
        data = note.to_dict()
        self.assertIs(type(data['user']), dict)
        
        with self.assertRaises(ModelError):
            note.update({'title': 1})

        with self.assertRaises(ModelError):
            note.update({'datetime': 1})

        self.assertDictEqual(
            data, note,
            f"Data must be the same if there is any error")

        update = {'title': 'New Title', 'content': 'New Note'}
        data.update(update)
        note.update(update)
        self.assertDictEqual(data, note.to_dict())


class TestField(unittest.TestCase):

    def setUp(self):
        self.model = MockUp({'required': True})

    def test_anyof(self):
        self.model['anyof'] = 1
        with self.assertRaises(ModelError):
            self.model['anyof'] = 5

    def test_verify(self):
        self.model['verify'] = '11fadebb-3c70-47a9-a3f0-ebf2a3815993'

    def test_default(self):
        self.assertEqual(self.model['default'], 'default')

    def test_length(self):
        self.model['length'] = 'hello'
        with self.assertRaises(ModelError):
            self.model['length'] = 'length-more-than-10'

    def test_listof(self):
        str_list = ['ab', 'cd']
        self.model['listof'] = str_list
        with self.assertRaises(ModelError):
            self.model['listof'] = [1, 2]
        self.assertEqual(self.model['listof'], str_list)

    def test_search(self):
        self.model['search'] = '0123456789'
        search = self.model['search']
        with self.assertRaises(ModelError):
            self.model['search'] = 'a'
        self.assertEqual(self.model['search'], search)

    def test_min(self):
        self.model['min'] = 1
        with self.assertRaises(ModelError):
            self.model['min'] = -1
        self.assertEqual(self.model['min'], 1)

    def test_max(self):
        self.model['max'] = 10
        with self.assertRaises(ModelError):
            self.model['max'] = 11
        self.assertEqual(self.model['max'], 10)

    def test_required(self):
        required = self.model['required']
        with self.assertRaises(ModelError):
            self.model['required'] = None
        self.assertEqual(self.model['required'], required)

    def test_subset(self):
        subset = [1, 2]
        self.model['subset'] = subset
        with self.assertRaises(ModelError):
            self.model['subset'] = [3, 4]
        self.assertEqual(self.model['subset'], subset)

    def test_type(self):
        string = 'test'
        self.model['type'] = string
        with self.assertRaises(ModelError):
            self.model['type'] = 1
            self.assertEqual(self.model['type'], string)

    def test_json(self):
        data = json.dumps(self.model)
        self.assertIsInstance(data, str)


class TestSubClass(unittest.TestCase):
    def setUp(self):
        class Content(Model):
            content_type = Field().type(str)

        class HTML(Content):
            pass

        self.html = HTML()

    def test_subclass(self):
        with self.assertRaises(ModelError):
            self.html['content_type'] = 1


if __name__ == '__main__':
    unittest.main()
