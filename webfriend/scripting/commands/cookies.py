from __future__ import absolute_import
from webfriend.scripting.commands.base import CommandProxy
from webfriend import exceptions


class CookiesProxy(CommandProxy):
    def all(self, urls=None):
        """
        Return a list of all cookies, optionally restricted to just a specific URL.

        #### Arguments

        - **urls** (`list`, optional):
            If specified, this is a list of URLs to retrieve cookies for.

        #### Returns
        A `list` of `dict` objects containing definitions for each cookie.
        """
        return [
            c.as_dict() for c in self.tab.network.get_cookies(urls)
        ]

    def query(self, name=None, **filters):
        """
        Query all known cookies and return a list of cookies matching those with specific values.

        #### Arguments

        The first argument (optional) is the name of the cookie as defined in its description. All
        options fields are taken as additional filters used to further restrict which cookies are
        returned.

        - **value** (`str`, optional):

            The value of the cookie.

        - **domain** (`str`, optional):

            The domain for which the cookie is valid for.

        - **path** (`str`, optional):

            The path valid of the cookie.

        - **expires** (`int`, optional):

            Cookie expiration date as the number of seconds since the UNIX epoch.

        - **size** (`int`, optional):

            The size of the cookie, in bytes.

        - **httpOnly** (`bool`, optional):

            Whether the cookie is marked as "HTTP only" or not.

        - **secure** (`bool`, optional):

            Whether the cookie is marked as secure or not.

        - **session** (`bool`, optional):

            Whether the cookie is marked as a session cookie or not.

        - **sameSite** (`bool`, optional):

            Whether the cookie is marked as a sameSite cookie or not.

        #### Returns
        A `list` of `dicts` describing the cookies that matched the given query, whose fields
        will be the same as the ones described above.
        """
        if name is not None:
            filters['name'] = name

        def _filter(cookie):
            for k, v in filters.items():
                if v is not None:
                    if cookie.get(k) != v:
                        return False

            return True

        return [
            c for c in self.all() if _filter(c)
        ]

    def get(self, name, domain=None):
        """
        Retrieve a specific cookie by name and (optionally) domain.  The domain should be provided
        to ensure the cookie returns at most one result.

        #### Arguments

        - **domain** (`str`, optional):

            The domain value of the cookie being retrieved to ensure an unambiguous result.

        #### Returns
        A `dict` describing the cookie returned, or `None`.

        #### Raises
        A `webfriend.exceptions.TooManyResults` exception if more than one cookie matches the given
        values.
        """
        results = self.query(name=name, domain=domain)

        if not len(results):
            return None
        elif len(results) == 1:
            return results[0]
        else:
            raise exceptions.TooManyResults(
                "Cookie name '{}' is ambiguous, {} cookies matched. Provide a more specific filter"
                " using {}::query".format(
                    name,
                    len(results),
                    self.as_qualifier()
                )
            )

    def delete(self, name, domain=None):
        """
        Delete the cookie specified by the given **name** and (optionally) **domain**.

        #### Arguments

        - **name** (`str`, optional):

            The name of the cookie to delete.

        - **domain** (`str`, optional):

            The domain value of the cookie being retrieved to ensure an unambiguous result.
        """
        if domain is None:
            cookie_by_name = self.get(name)
            domain = cookie_by_name.get('domain')

        self.tab.network.delete_cookie(domain, name)

    # def set_cookie(
    #     self,
    #     url,
    #     name,
    #     value,
    #     domain=None,
    #     path=None,
    #     secure=None,
    #     http_only=None,
    #     same_site=None,
    #     expires=None
    # ):
    def set(self, name, **kwargs):
        """
        Create or update a cookie based on the given values.

        #### Arguments

        - **name** (`str`):

            The name of the cookie to set.

        - **value** (any):

            The value to set in the cookie.

        - **url** (`str`, optional):

            The URL to associate the cookie with. This is important when dealing with things like
            host-only cookies (if **domain** isn't set, a host-only cookie will be created.)  In
            this case, the cookie will only be valid for the exact URL that was used.

            The default value is the URL of the currently active tab.

        - **domain** (`str`, optional):

            The domain for which the cookie will be presented.

        - **path** (`str`, optional):

            The path value of the cookie.

        - **secure** (`bool`, optional):

            Whether the cookie is flagged as secure or not.

        - **http_only** (`bool`, optional):

            Whether the cookie is flagged as an HTTP-only cookie or not.

        - **same_site** (`str`, optional):

            Sets the "Same Site" attribute of the cookie.  The value "strict" will restrict any
            cross-site usage of the cookie.  The value "lax" allows top-level navigation changes
            to receive the cookie.

        - **expires** (`int`, optional):

            Specifies when the cookie expires in epoch seconds (number of seconds
            since 1970-01-01 00:00:00 UTC).
        """
        if not kwargs.get('url', None):
            kwargs['url'] = self.tab.url

        if kwargs.get('same_site', None):
            kwargs['same_site'] = kwargs['same_site'].title()

        if not kwargs.get('value', None):
            raise ValueError("'value' option must be specified")

        return self.tab.network.set_cookie(**kwargs)
