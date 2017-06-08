from __future__ import absolute_import
from . import CommandProxy
from ... import exceptions


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
        if domain is None:
            cookie_by_name = self.get(name)
            domain = cookie_by_name.get('domain')

        self.tab.network.delete_cookie(domain, name)

    def set(self, name, **kwargs):
        """
        See: `webfriend.rpc.network.set_cookie`
        """
        if not kwargs.get('url', None):
            raise ValueError("'url' option must be specified")

        if not kwargs.get('value', None):
            raise ValueError("'value' option must be specified")

        return self.tab.network.set_cookie(**kwargs)
