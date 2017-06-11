from __future__ import absolute_import
from webfriend.scripting.commands.base import CommandProxy
# from webfriend import exceptions
from webfriend.utils import autotype
from webfriend.scripting.parser import types


class FormatProxy(CommandProxy):
    qualifier = 'fmt'
    doc_name = 'Format'

    def autotype(self, value):
        """
        Takes a string value and attempts to automatically determines the data type.

        #### Arguments

        - **value** (`str`):

            The value to apply the operation to.

        #### Returns
        The value converted to the automatically-detected type, or the original unmodified value if
        a type could not be determined.
        """
        return autotype(value)

    def strip(self, value, characters=None):
        """
        Removes the whitespace or a set of given characters from the leading and trailing ends of
        the given string.

        #### Arguments

        - **value** (`str`):

            The value to apply the operation to.

        - **characters** (`str`, optional):

            If specified, any of these characters will be trimmed from the string instead of
            whitespace.

        #### Returns
        The trimmed string.
        """
        if isinstance(value, basestring):
            return value.strip(characters)
        return value

    def lstrip(self, value, characters=None):
        """
        Removes the whitespace or a set of given characters from the leading end of the
        given string.

        #### Arguments

        - **value** (`str`):

            The value to apply the operation to.

        - **characters** (`str`, optional):

            If specified, any of these characters will be trimmed from the string instead of
            whitespace.

        #### Returns
        The trimmed string.
        """
        if isinstance(value, basestring):
            return value.lstrip(characters)
        return value

    def rstrip(self, value, characters=None):
        """
        Removes the whitespace or a set of given characters from the trailing end of the
        given string.

        #### Arguments

        - **value** (`str`):

            The value to apply the operation to.

        - **characters** (`str`, optional):

            If specified, any of these characters will be trimmed from the string instead of
            whitespace.

        #### Returns
        The trimmed string.
        """
        if isinstance(value, basestring):
            return value.rstrip(characters)
        return value

    def lower(self, value):
        """
        Returns the given string with all characters replaced with their lowercase variants.

        #### Arguments

        - **value** (`str`):

            The value to apply the operation to.

        #### Returns
        The lowercased string.
        """
        if isinstance(value, basestring):
            return value.lower()
        return value

    def upper(self, value):
        """
        Returns the given string with all characters replaced with their uppercase variants.

        #### Arguments

        - **value** (`str`):

            The value to apply the operation to.

        #### Returns
        The uppercased string.
        """
        if isinstance(value, basestring):
            return value.upper()
        return value

    def title(self, value):
        """
        Returns the given string with the first character of each whitespace-separated word
        capitalized.

        #### Arguments

        - **value** (`str`):

            The value to apply the operation to.

        #### Returns
        The title-cased string.
        """
        if isinstance(value, basestring):
            return value.title()
        return value

    def replace(self, value, find, replace, count=None):
        """
        Locates a given string or pattern in the given string and replaces occurrences with the
        given replacement value.

        #### Arguments

        - **value** (`str`):

            The value to apply the operation to.

        - **find** (`str`, `regex`):

            The exact string or regular expression that will match the given **value**.

        - **replace** (`str`):

            The string (or string pattern for regular expression) that will replace occurrences in
            the given **value**.

            If **find** is a regular expression, then **replace** is interpreted as follows:

            - Groups in the regular expression can be referenced numerically with backreferences
              like `\\1`, `\\3`.  The number following the backslash refers to the _nth_ group in
              the **find** expression, where group numbering starts from 1.  The `\\0`
              backreference refers to the entire matched substring.

            - Named captures in **find** can be referenced such that `\\g<name>` refers to named
              capture group `name` in **find** (which would be specified as `(?P<name>...)`.)

        - **count** (`int`, optional):

            If specified, up to this many occurrences will be matched before matching stops.  Use
            this to limit the number of replacement operations that can occur.

        #### Returns
        The resulting string with all replacements (if any) applied.
        """
        if isinstance(find, types.RegularExpression):
            if isinstance(count, int):
                return find.rx.sub(replace, value, count=count)
            else:
                return find.rx.sub(replace, value)
        else:
            return value.replace(find, replace, count)

    def split(self, value, on, count=None):
        """
        Split an input string into a list of strings.

        #### Arguments

        - **value** (`str`):

            The value to apply the operation to.

        - **on** (`str`):

            The character or substring to split **value** on.  This value will be
            discarded from the resulting list of strings.

        - **count** (`int`, optional):

            If specified, only perform up to this many splits before returning the remaining
            unsplit string as the final element in the list.

        #### Returns
        A `list` of at least 1 element.
        """
        return value.split(on, count)

    def rsplit(self, value, on, count=None):
        """
        Split an input string into a list of strings, starting from the right-hand side.

        #### Arguments

        - **value** (`str`):

            The value to apply the operation to.

        - **on** (`str`):

            The character or substring to split **value** on.  This value will be
            discarded from the resulting list of strings.

        - **count** (`int`, optional):

            If specified, only perform up to this many splits before returning the remaining
            unsplit string as the final element in the list.

        #### Returns
        A `list` of at least 1 element.
        """
        return value.rsplit(on, count)

    def join(self, values, joiner=','):
        """
        Join a list of values into a single string.

        #### Arguments

        - **values** (`list`):

            A list of values (of any type) to stringify and join by a given joiner string.

        - **joiner** (`str`):

            The string to join list elements by.

        #### Returns
        The resulting joined string.
        """
        if not isinstance(values, (list, tuple)):
            values = [values]

        values = ['{}'.format(v) for v in values]

        return joiner.join(values).encode('UTF-8')
