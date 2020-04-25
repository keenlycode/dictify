import re
from typing import Callable
from functools import wraps


class Function:
    def __init__(self, func, *args, **kw):
        self.func = func
        self.args = args
        self.kw = kw
    
    def __call__(self, field, value):
        self.func(field, value, *self.args, **self.kw)

    def __repr__(self):
        return f"{self.func.__name__}{self.args}{self.kw}"


def function(func: Callable):
    """Decorator used in Field class to add methods in validation chain"""
    @wraps(func)
    def wrapper(self, *args, **kw):
        # Test default value.
        if self.default != UNDEF:
            try:
                func(self, self.default, *args, **kw)
            except Exception as error:
                raise Field.DefineError(
                    f"Field(default={self.default}) conflict with ",
                    f"{func.__name__}(*{args}, **{kw})", error)
        
        # Keep function in chain.
        self._functions.append(Function(func, *args, **kw))
        return self
    return wrapper


class UNDEF:
    """Create ```UNDEF`` value"""
    def __repr__(self):
        return 'UNDEF'


#: undefined value
UNDEF = UNDEF()


class ListOf(list):
    """Modified list to check it's members instance.

    Parameters
    ----------
    value:
        Value for validation it's type with ``type_``.
    type_:
        Type for validation with ``value``
    """
    def __init__(self, value, type_):
        self._type = type_
        errors = list()
        for v in value:
            if not isinstance(v, self._type):
                errors.append(
                    AssertionError(f"'{v}' is not instance of {self._type}")
                )
        if errors:
            raise ListOf.ValueError(errors)
        super().__init__(value)

    class ValueError(Exception):
        pass

    def __setitem__(self, index, value):
        """Set list value at ``index`` if ``value`` is valid"""
        assert isinstance(value, self._type),\
            f"'{value}' is not instance of {self._type}"
        return super().__setitem__(index, value)

    def append(self, value):
        """Append object to the end of the list if ``value`` is valid."""
        assert isinstance(value, self._type),\
            f"'{value}' is not instance of {self._type}"
        return super().append(value)


class Field:
    """Create ``Field()`` object which can validate it's value.
    Can be defined in class ``Model``.

    Examples
    --------
    ::

        # Use with validators.
        field = Field(required=True).anyof(['AM','PM'])
        field.value = 'AM'
        field.value = 'A'  # This will raise Field.VerifyError

        # Chained validators.
        field = Field(default=0).instance(str).search('.*@.*)
        field.value = 5
        field.value = -1  # This will raise Field.VerifyError

    Notes
    -----
        As the examples, when defining ``Field()`` validation with it's methods
        below. The first arguments ``(value)`` can be omitted since it will be
        put automatically while validating value.
    ...

    Parameters
    ----------
    required: bool=False
        Required option. If set to ``True``, call ``Field().value`` without
        assigned value will raise ``Field.RequiredError``
    disallow: list=[]
        List of disallowed value.
    default: any=UNDEF
        Field's default value
    """

    class VerifyError(Exception):
        """Error to be raised if ``Field().value`` doesn't pass validation.
        """
        pass

    class RequiredError(Exception):
        """Error to be raised if ``Field(required=True)``
        but no value provided.
        """
        pass

    class DefineError(Exception):
        """Error to be raised when defining ``Field()``."""
        pass

    def __init__(
            self, required: bool = False,
            default=UNDEF, disallow: list = []):
        self.required = required
        self._default = default
        self.disallow = disallow
        if self.default in self.disallow:
            raise Field.DefineError(
                f"Default value is disallowed. " +\
                f"default({self.default}), " +\
                f"disallow({self.disallow})"
            )
        self._functions = list()
        self._value = self.default

    @property
    def default(self):
        """Field's default value"""
        if callable(self._default):
            return self._default()
        else:
            return self._default

    @property
    def value(self):
        """``Field()``'s value"""
        if self.required and self._value == UNDEF:
            raise Field.RequiredError('Field is required')
        return self._value

    @value.setter
    def value(self, value):
        errors = list()
        if self.required and value == UNDEF:
            raise Field.RequiredError('Field is required')
        if value in self.disallow:
            raise Field.VerifyError(
                f"Value ({value}) is not allowed. " +\
                f"Disallow {self.disallow}")
        for function in self._functions:
            try:
                function(self, value)
            except Exception as e:
                errors.append((function, e))
        if errors:
            raise Field.VerifyError(errors)
        self._value = value

    def reset(self):
        """Reset ``Field().value`` to default or ``UNDEF``"""
        self._value = self.default

    @function
    def instance(self, value, type_: type):
        """Verify that ``value`` is instance to ``type_``
        
        ``assert isinstance(value, type_)``
        """
        assert isinstance(value, type_),\
            f'{type(value)} is not instance of {type_}'

    @function
    def listof(self, value, type_):
        """Verify that ``Field()`` value is a list of ``type_``"""
        ListOf(value, type_)

    @function
    def match(self, value, re_: str, flags=0):
        """Match value with regular expression string ``re_``."""
        assert re.match(re_, value, flags),\
            f"Matching with re.match('{re_}', '{value}') is None"

    @function
    def model(self, value, model_cls: 'Model'):
        """Verify that value pass ``model_cls`` validation."""
        model_cls(value)

    @function
    def search(self, value, re_: str, flags=0):
        """Search value with with regular expression string ``re_``."""
        assert re.search(re_, value, flags),\
            f"Searching with re.search('{re_}', '{value}') is None"

    @function
    def verify(self, value, func, message=None):
        """Designed to use with ``lambda`` for simple syntax since ``lambda``
        can't use ``assert`` statement.
        
        The callable must return ``True`` or ``False``.

        If return ``False``, It will be raised as ``AssertionError``.

        Example
        -------
        ::

            # Verify that username is `str` instance and has length <= 20
            username = Field().instance(str).verify(
                lambda value: len(value) <= 20,
                f'username length must <= 20'
            )

            username.value = 'user-1'  # Valid.
            username.value = 1  # Invalid.
            username.value = 'username-which-longer-than-20-characters'  # Invalid.
        """
        assert func(value), message

    @function
    def func(self, value, fn):
        """Use callable function to validate value.
        
        ``fn`` will be called later as ``fn(value)`` and should return
        ``Exception`` if value is invalid.

        Examples
        --------
        ::

            def is_uuid4(value):
                id = uuid.UUID(value)
                # Raise AssertionError if id.version != 4
                assert id.version == 4

            uuid4 = Field().func(is_uuid4)
        """
        fn(value)


class Model(dict):
    """Modified ``dict`` that can defined ``Field`` in it's class.

    Examples
    --------
    ::

        class Note(Model):
            title = Field(required=True).instance(str)
            content = Field().instance(str)
            datetime = Field(default=datetime.utcnow()).instance(datetime)

        note = Note({'title': 'Title'})

    Parameters
    ----------
    data: dict
        Model's data
    """

    def __init__(self, data=dict()):
        assert isinstance(data, dict),\
            f"Model initial data shold be instance of dict"
        data = data.copy()
        self._field = dict()
        for key in self.__dir__():
            field = self.__getattribute__(key)
            # Verify that item is Field().
            if not isinstance(field, Field):
                continue
            # If default option is set in Field(), set default value
            if (field.default != UNDEF) and (key not in data):
                data[key] = field.value
            # If required option is set in Field(), check if it's provided.
            elif field.required:
                if key not in data:
                    raise Model.Error({
                        key: KeyError("This field is required")
                    })
            # Keep Field() in self._field for data validation.
            self._field[key] = field
        self._validate(data)
        super().__init__(data)

    class Error(Exception):
        """``Exception`` when data doesn't pass ``Model`` validation.

        Parameters
        ----------
        message: str
            Error message. Format: ``{'field': Field.Error([Exception,])}``
        """
        pass

    def __delitem__(self, key):
        """Delete item but also check for Field's default or required option
        to make sure that Model's data is valid.
        """
        if self._field[key].default != UNDEF:
            self[key] = self._field[key].default
        elif self._field[key].required:
            raise Model.Error({
                key: Field.RequiredError("Field is required")})
        else:
            return super().__delitem__(key)

    def __setitem__(self, key, value):
        """Set ``value`` if is valid."""
        error = None
        try:
            self._field[key].value = value
            super().__setitem__(key, self._field[key].value)
        except KeyError:
            error = {key: KeyError('Field is not defined')}
        except (Field.VerifyError, ListOf.ValueError) as e:
            error = {key: e}
        if error:
            raise Model.Error(error)

    def _validate(self, data: dict):
        error = dict()
        for key in data:
            try:
                self._field[key].value = data[key]
                self._field[key].reset()
            except KeyError:
                error[key] = KeyError('Field is not defined')
            except Field.VerifyError as e:
                error[key] = e
        if error:
            raise Model.Error(error)

    def update(self, data):
        """Update ``data`` if is valid."""
        assert isinstance(data, dict)
        data = data.copy()
        self._validate(data)
        return super().update(data)
