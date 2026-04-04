"""Behavioral tests for the public dictify validation API."""

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any, cast

import pytest

from dictify import UNDEF, Field, ListOf, Model


def datetime_verify(value):
    datetime.fromisoformat(value)


def uuid4_verify(value):
    try:
        id_ = uuid.UUID(value)
    except AttributeError as exc:
        raise AttributeError("Can't parse value to UUID") from exc
    assert id_.version == 4, f"Value is UUID v{id_.version}, not v4"


class User(Model):
    id = Field(default=lambda: uuid.uuid4()).instance(uuid.UUID)
    name = Field(required=True).instance(str)


class Comment(Model):
    content = Field().instance(str)
    datetime = Field(default=lambda: datetime.now(timezone.utc)).instance(datetime)
    user = Field(required=True).instance(User)


class Note(Model):
    title = Field(required=True).instance(str)
    content = Field().instance(str)
    datetime = Field(default=lambda: datetime.now(timezone.utc)).instance(datetime)
    user = Field(required=True).instance(User)
    comments = Field().listof(Comment)

    def post_validate(self):
        assert self.get("title") != self.get("content")


class UserJSON(Model):
    id = Field(default=lambda: str(uuid.uuid4())).func(uuid4_verify)
    name = Field(required=True).instance(str)


class CommentJSON(Model):
    content = Field(required=True).instance(str)
    datetime = Field(default=lambda: datetime.now(timezone.utc).isoformat()).func(
        datetime_verify
    )
    user = Field(required=True).model(UserJSON)


class NoteJSON(Model):
    title = Field(required=True).instance(str)
    content = Field().instance(str)
    datetime = Field(default=lambda: datetime.now(timezone.utc).isoformat()).func(
        datetime_verify
    )
    user = Field(required=True).model(UserJSON)
    comments = Field().listof(CommentJSON)


@pytest.fixture
def note():
    return Note(
        {
            "title": "Title",
            "content": "Content",
            "datetime": datetime.now(timezone.utc),
            "user": User({"id": uuid.uuid4(), "name": "user1"}),
            "comments": [
                Comment(
                    {
                        "content": "second user comment",
                        "user": User({"name": "second user"}),
                    }
                ),
                Comment(
                    {
                        "content": "third user comment",
                        "user": User({"name": "third user"}),
                    }
                ),
            ],
        }
    )


def test_init(note):
    with pytest.raises(AssertionError):
        Note(cast(Any, []))

    with pytest.raises(Model.Error):
        Note({})

    default_note = Note({"title": "Title", "user": User({"name": "user1"})})
    assert isinstance(default_note["datetime"], datetime)

    data = {
        "title": "Title",
        "content": "Content",
        "datetime": datetime.now(timezone.utc),
        "user": User({"id": uuid.uuid4(), "name": "user-1"}),
    }
    fresh_note = Note(data)
    assert fresh_note == data
    assert note["title"] == "Title"
    assert isinstance(dict(fresh_note), dict)


def test_model_fields_are_isolated_per_instance():
    first = User({"name": "first"})
    second = User({"name": "second"})

    assert first._bound_fields["name"] is not second._bound_fields["name"]
    assert first._bound_fields["name"].definition is User.name
    assert second._bound_fields["name"].definition is User.name

    with pytest.raises(Field.RequiredError):
        User.name.value


def test_strict(note):
    strict_note = dict(note)
    strict_note["undefined_key"] = 1
    with pytest.raises(Model.Error):
        Note(strict_note, strict=True)

    del strict_note["undefined_key"]
    strict_model = Note(strict_note, strict=True)
    with pytest.raises(Model.Error):
        strict_model["undefined_key"] = 1

    relaxed_note = dict(note)
    relaxed_note["undefined_key"] = 1
    relaxed_model = Note(relaxed_note, strict=False)
    assert relaxed_model["undefined_key"] == 1

    del relaxed_model["undefined_key"]
    relaxed_model["undefined_key"] = 1
    assert relaxed_model["undefined_key"] == 1


def test_delitem(note):
    del note["datetime"]
    assert isinstance(note["datetime"], datetime)

    title = note["title"]
    with pytest.raises(Model.Error):
        del note["title"]
    assert title == note["title"]

    del note["content"]
    assert "content" not in note


def test_setitem(note):
    data = dict(note)

    with pytest.raises(Model.Error):
        note["title"] = 0

    with pytest.raises(Model.Error):
        note["datetime"] = "today"

    assert note == data

    title = "New Title"
    note["title"] = title
    assert note["title"] == title


def test_json():
    note = NoteJSON({"title": "Note JSON", "user": UserJSON({"name": "user-1"})})
    note_data = json.loads(json.dumps(note.dict()))
    NoteJSON(note_data)


def test_update():
    note = Note({"title": "Title", "user": User({"name": "user example"})})
    data = note.dict()
    assert isinstance(data["user"], dict)

    with pytest.raises(Model.Error):
        note.update({"title": 1})

    with pytest.raises(Model.Error):
        note.update({"datetime": 1})

    assert data == note.dict()

    update = {"title": "New Title", "content": "New Note"}
    data.update(update)
    note.update(update)
    assert data == note.dict()


def test_setdefault():
    note = Note({"title": "Title", "user": User({"name": "user example"})})

    assert note.setdefault("title", "Ignored") == "Title"
    assert note["title"] == "Title"

    assert note.setdefault("content", "New Note") == "New Note"
    assert note["content"] == "New Note"

    relaxed = Note(
        {"title": "Title", "user": User({"name": "user example"})}, strict=False
    )
    assert relaxed.setdefault("extra", 1) == 1
    assert relaxed["extra"] == 1

    strict = Note(
        {"title": "Title", "user": User({"name": "user example"})}, strict=True
    )
    with pytest.raises(Model.Error):
        strict.setdefault("extra", 1)


def test_field_init():
    field = Field()
    assert isinstance(field, Field)
    assert field._value is UNDEF

    field = Field(required=True, default="default", grant=[None])
    assert field.required is True
    assert field._default == "default"


def test_field_default():
    field = Field(default="default")
    assert field.value == "default"
    field = Field(default=lambda: datetime.now(timezone.utc))
    assert isinstance(field.default, datetime)


def test_field_value():
    field = (
        Field(required=True, grant=[None])
        .instance(str)
        .verify(lambda value: len(value) <= 10)
    )

    with pytest.raises(Field.RequiredError):
        field.value

    field.value = "test"
    assert field.value == "test"

    with pytest.raises(Field.VerifyError):
        field.value = "word-length-more-than-ten"

    assert field.value == "test"

    field.value = None
    assert field.value is None


def test_field_reset():
    field = Field(default="default")
    field.value = 1
    field.reset()
    assert field.value == "default"


def test_field_func():
    field = Field().func(uuid4_verify)
    field.value = str(uuid.uuid4())
    with pytest.raises(Field.VerifyError):
        field.value = 1


def test_field_instance():
    field = Field().instance(str)
    field.value = "test"
    with pytest.raises(Field.VerifyError):
        field.value = 1


def test_field_listof():
    def less_than_five(value):
        assert value < 5

    field = Field().listof((int, float), validate=less_than_five)
    field.value = [1, 2]
    with pytest.raises(Field.VerifyError):
        field.value = ["a", "b"]

    with pytest.raises(Field.VerifyError):
        field.value = [1, 7]

    assert isinstance(field.value, ListOf)


def test_field_match():
    field = Field().match("012", re.I)
    field.value = "0123456789"
    with pytest.raises(Field.VerifyError):
        field.value = "123"
    assert field.value == "0123456789"


def test_field_model():
    field = Field().model(NoteJSON)
    note = NoteJSON({"title": "Note", "user": UserJSON({"name": "user-1"})})
    field.value = note

    note_data = json.loads(json.dumps(note.dict()))
    field.value = note_data

    with pytest.raises(Field.VerifyError):
        field.value = 1


def test_field_search():
    field = Field().search(r"\w+", re.I)
    field.value = "0123456789"
    with pytest.raises(Field.VerifyError):
        field.value = "?"
    assert field.value == "0123456789"


def test_subclass():
    class Content(Model):
        content_type = Field().instance(str)

    class HTML(Content):
        pass

    html = HTML()
    with pytest.raises(Model.Error):
        html["content_type"] = 1
