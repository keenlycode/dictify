import unittest
import json
import uuid
import re
from datetime import datetime
from dictify import ListOf, Model, Field, UNDEF


def datetime_verify(value):
    datetime.fromisoformat(value)


def uuid4_verify(value):
    try:
        id_ = uuid.UUID(value)
    except AttributeError:
        raise AttributeError(f"Can't parse value to UUID")
    assert id_.version == 4, f"Value is UUID v{id_.version}, not v4"


class User(Model):
    id = Field(default=lambda: uuid.uuid4()).instance(uuid.UUID)
    name = Field(required=True).instance(str)


class Comment(Model):
    content = Field().instance(str)
    datetime = Field(default=lambda: datetime.utcnow()).instance(datetime)
    user = Field(required=True).instance(User)


class Note(Model):
    title = Field(required=True).instance(str)
    content = Field().instance(str)
    datetime = Field(default=lambda: datetime.utcnow()).instance(datetime)
    user = Field(required=True).instance(User)
    comments = Field().listof(Comment)

    def post_validate(self):
        assert self.get('title') != self.get('content')


class UserJSON(Model):
    id = Field(default=lambda: str(uuid.uuid4())).func(uuid4_verify)
    name = Field(required=True).instance(str)


class CommentJSON(Model):
    content = Field(required=True).instance(str)
    datetime = Field(default=lambda: datetime.utcnow().isoformat())\
        .func(datetime_verify)
    user = Field(required=True).model(UserJSON)


class NoteJSON(Model):
    title = Field(required=True).instance(str)
    content = Field().instance(str)
    datetime = Field(default=lambda: datetime.utcnow().isoformat())\
        .func(datetime_verify)
    user = Field(required=True).model(UserJSON)
    comments = Field().listof(CommentJSON)


class TestModel(unittest.TestCase):

    def setUp(self):
        self.note = Note({
            'title': 'Title',
            'content': 'Content',
            'datetime': datetime.utcnow(),
            'user': User({
                'id': uuid.uuid4(),
                'name': 'user1'
            }),
            'comments': [
                Comment({
                    'content': 'second user comment',
                    'user': User({'name': 'second user'})
                }),
                Comment({
                    'content': 'third user comment',
                    'user': User({'name': 'third user'})
                })
            ]
        })

    def test_init(self):
        # Test when initial data is not type of dict.
        with self.assertRaises(AssertionError):
            Note([])

        # Test required field.
        with self.assertRaises(Model.Error):
            Note({})

        note = Note({
            'title': 'Title',
            'user': User({'name': 'user1'})
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
                'name': 'user-1'
            })
        }
        note = Note(data)
        self.assertDictEqual(note, data)

    def test_strict(self):
        """Test strict=True
        1. Raise error if create `Model` object with undefined field
        2. Raise error if set value to undefined field
        """

        note = dict(self.note)
        note['undefined_key'] = 1
        with self.assertRaises(Model.Error):
            note = Note(note, strict=True)

        del note['undefined_key']
        note = Note(note, strict=True)
        with self.assertRaises(Model.Error):
            note['undefined_key'] = 1


        """Test strict=False
        1. Can crate Model object with undefined field
        2. Can set value on undefined field
        """

        note = dict(self.note)
        note['undefined_key'] = 1
        note = Note(note, strict=False)
        self.assertEqual(note['undefined_key'], 1)

        del note['undefined_key']
        note = Note(note, strict=False)
        note['undefined_key'] = 1
        self.assertEqual(note['undefined_key'], 1)


    def test_delitem(self):
        """Test 3 cases:
        1. Delete field with default option.
        2. Delete field with required option.
        3. Delete field with no option.
        """
        # 1. Delete field with default option.
        del self.note['datetime']
        self.assertIsInstance(self.note['datetime'], datetime)

        # 2. Delete field with required option.
        title = self.note['title']
        with self.assertRaises(Model.Error):
            del self.note['title']
        self.assertEqual(title, self.note['title'])

        # 3. Delete field with no option.
        del self.note['content']
        self.assertNotIn('content', self.note)

    def test_setitem(self):
        """Test `__setitem__` for 4 cases:
        1. Model.Error,
        2. Key Error
        3. Data unmodified if there is any error.
        4. Success.
        """
        data = self.note.copy()

        # 1. Model.Error
        with self.assertRaises(Model.Error):
            self.note['title'] = 0

        # 2. KeyError
        with self.assertRaises(Model.Error):
            self.note['datetime'] = 'today'

        # 3. Data unmodified if there is any error.
        self.assertDictEqual(
            self.note, data, "Data must be unmodified if error")

        # 4. Success.
        title = 'New Title'
        self.note['title'] = title
        self.assertEqual(self.note['title'], title)

    def test_json(self):
        note = NoteJSON({
            'title': 'Note JSON',
            'user': UserJSON({'name': 'user-1'})
        })
        note = json.dumps(note)
        note = json.loads(note)
        NoteJSON(note)

    def test_post_validate(self):
        pass
        # with self.assertRaise(AssertionError):
        #     self.note['title'] = self.note['content']

    def test_update(self):
        note = Note({
            'title': 'Title',
            'user': User({'name': 'user example'})
        })
        data = note.copy()
        self.assertIsInstance(data['user'], dict)

        with self.assertRaises(Model.Error):
            note.update({'title': 1})

        with self.assertRaises(Model.Error):
            note.update({'datetime': 1})

        self.assertDictEqual(
            data, note,
            f"Data must be unmodified if error")

        update = {'title': 'New Title', 'content': 'New Note'}
        data.update(update)
        note.update(update)
        self.assertDictEqual(data, note)


class TestField(unittest.TestCase):
    def test_init(self):
        # 1. Field with no options
        field = Field()
        self.assertIsInstance(field, Field)
        self.assertEqual(field._value, UNDEF)

        # 2. Field with options.
        field = Field(required=True, default='default', grant=[None])
        self.assertEqual(field.required, True)
        self.assertEqual(field._default, 'default')

    def test_default(self):
        field = Field(default='default')
        self.assertEqual(field.value, 'default')
        field = Field(default=datetime.utcnow)
        self.assertIsInstance(field.default, datetime)

    def test_value(self):
        field = Field(required=True, grant=[None])\
            .instance(str).verify(lambda value: len(value) <= 10)

        # Required Field should raise RequiredError if ask for value
        # before assigned.
        with self.assertRaises(Field.RequiredError):
            field.value

        # Assign valid value.
        field.value = 'test'
        self.assertEqual(field.value, 'test')

        # Assign not valid value.
        with self.assertRaises(Field.VerifyError):
            field.value = 'word-length-more-than-ten'

        # field.value should be unmodifed if errors.
        self.assertEqual(field.value, 'test')

        # Assign ignored value.
        field.value = None
        assert field.value is None

    def test_reset(self):
        field = Field(default='default')
        field.value = 1
        field.reset()
        self.assertEqual(field.value, 'default')

    def test_func(self):
        field = Field().func(uuid4_verify)
        # Assign valid value.
        field.value = str(uuid.uuid4())
        # Assign not valid value.
        with self.assertRaises(Field.VerifyError):
            field.value = 1

    def test_instance(self):
        field = Field().instance(str)
        field.value = 'test'
        with self.assertRaises(Field.VerifyError):
            field.value = 1

    def test_listof(self):
        def less_than_five(value):
            assert value < 5

        field = Field().listof((int, float), validate=less_than_five)
        str_list = [1, 2]
        field.value = str_list
        with self.assertRaises(Field.VerifyError):
            field.value = ['a', 'b']

        with self.assertRaises(Field.VerifyError):
            field.value = [1, 7]

        # Field's value should be instance of `ListOf`
        self.assertIsInstance(field.value, ListOf)

    def test_match(self):
        field = Field().match('012', re.I)
        field.value = '0123456789'
        with self.assertRaises(Field.VerifyError):
            field.value = '123'
        self.assertEqual(field.value, '0123456789')

    def test_model(self):
        field = Field().model(NoteJSON)
        note = NoteJSON({
            'title': 'Note',
            'user': UserJSON({'name': 'user-1'})
        })
        # 1. Set field value to NoteJSON() instance
        field.value = note

        # 2. Set field value to dict() which is JSON compatible.
        note = json.dumps(note)
        note = json.loads(note)
        field.value = note

        # 3. Error if assign invalid value.
        with self.assertRaises(Field.VerifyError):
            field.value = 1

    def test_search(self):
        field = Field().search(r'\w+', re.I)
        field.value = '0123456789'
        with self.assertRaises(Field.VerifyError):
            field.value = '?'
        self.assertEqual(field.value, '0123456789')


class TestSubClass(unittest.TestCase):
    def setUp(self):
        class Content(Model):
            content_type = Field().instance(str)

        class HTML(Content):
            pass

        self.html = HTML()

    def test_subclass(self):
        with self.assertRaises(Model.Error):
            self.html['content_type'] = 1


if __name__ == '__main__':
    unittest.main()
