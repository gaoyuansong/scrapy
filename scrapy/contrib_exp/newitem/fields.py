import datetime
import decimal
import re


__all__ = ['MultiValuedField', 'BooleanField', 'DateField', 'DecimalField',
           'FloatField', 'IntegerField', 'StringField']


class FieldValueError(Exception):
    pass


class BaseField(object):
    def __init__(self, required=False, default=None):
        self.required = required
        self.default = default or self.to_python(None)

    def assign(self, value):
        return self.to_python(value)

    def to_python(self, value):
        """
        Converts the input value into the expected Python data type.
        Subclasses should override this.
        """
        return value


class Field(BaseField):
    def assign(self, value):
        if hasattr(value, '__iter__'):
            return self.to_python(self.deiter(value))
        else:
            return self.to_python(value)

    def deiter(self, value):
        "Converts the input iterable into a single value."
        return ' '.join(value)


class MultiValuedField(BaseField):
    def __init__(self, field_type, required=False, default=None):
        self._field = field_type()
        super(MultiValuedField, self).__init__(required, default)

    def to_python(self, value):
        if value is None:
            return []
        else:
            return [self._field.to_python(v) for v in value]


class BooleanField(Field):
    def to_python(self, value):
        return bool(value)


ansi_date_re = re.compile(r'^\d{4}-\d{1,2}-\d{1,2}$')


class DateField(Field):
    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value

        if not ansi_date_re.search(value):
            raise FieldValueError(
                "Enter a valid date in YYYY-MM-DD format.")

        year, month, day = map(int, value.split('-'))
        try:
            return datetime.date(year, month, day)
        except ValueError, e:
            raise FieldValueError("Invalid date: %s" % str(e))


class DecimalField(Field):
    def to_python(self, value):
        if value is None:
            return value
        try:
            return decimal.Decimal(value)
        except decimal.InvalidOperation:
            raise FieldValueError("This value must be a decimal number.")


class FloatField(Field):
    def to_python(self, value):
        if value is None:
            return value
        try:
            return float(value)
        except (TypeError, ValueError):
            raise FieldValueError("This value must be a float.")


class IntegerField(Field):
    def to_python(self, value):
        if value is None:
            return value
        try:
            return int(value)
        except (TypeError, ValueError):
            raise FieldValueError("This value must be an integer.")


class StringField(Field):
    def to_python(self, value):
        if isinstance(value, basestring):
            return value
        if value is None:
            return value
        raise FieldValueError("This field must be a string.")
