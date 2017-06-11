from __future__ import absolute_import
import inspect
import logging
import re
import webfriend.scripting.commands
from webfriend.scripting.environment import Environment
from webfriend.scripting.scope import Scope
from webfriend.scripting.commands.base import CommandProxy
from webfriend.utils import get_module_from_string, resolve_object

RX_DOCSTRING_SEEOTHER = re.compile('(?P<head>.*)\s*see:\s*`(?P<module>.*)`\s*(?P<tail>.*)', re.IGNORECASE)


def document_commands(plugins=None, only_plugins=False, omit_header=False):
    base = CommandProxy
    environment = Environment(Scope())
    toc = []
    subtoc = {}
    commands_body = []

    if isinstance(plugins, list):
        for plugin in plugins:
            environment.register_by_module_name(plugin)

    classes = environment.proxies

    classes = [
        i for q, i in classes.items() if q == CommandProxy.default_qualifier
    ] + sorted([
        i for q, i in classes.items() if q != CommandProxy.default_qualifier
    ])

    # for each proxy class
    for proxy in classes:
        if only_plugins:
            if plugins is None:
                continue

            if isinstance(plugins, list) and proxy.as_qualifier() not in plugins:
                continue

        proxy_docs = inspect.getdoc(proxy)
        commands_body.append("## `{}` Command Set".format(proxy.as_qualifier()))
        commands_body.append('')

        # add top-level TOC item for this command set
        if proxy.doc_name:
            toc_title = proxy.doc_name
        else:
            toc_title = proxy.as_qualifier().title()

        tocentry = (toc_title, proxy.as_qualifier())

        if tocentry not in toc:
            toc.append(tocentry)

        subtoc[proxy.as_qualifier()] = set()

        # add command set documentation (if any)
        if proxy_docs:
            commands_body.append(proxy_docs)
            commands_body.append('')

        # for each direct method of this proxy (omitting private and inherited methods)
        for method in inspect.getmembers(proxy, inspect.ismethod):
            if method[0].startswith('_'):
                continue

            if method[0] in dir(base):
                continue

            # get method documentation
            method_doc = get_docstring(method[1])

            commands_body.append("### `{}`".format(proxy.qualify(method[0])))

            # add method
            subtoc[proxy.as_qualifier()].add(
                (proxy.qualify(method[0]), (method_doc is not None))
            )

            commands_body.append("\n```\n{}{}\n```".format(
                proxy.qualify(''),
                get_signature(method)
            ))

            if method_doc:
                commands_body.append('')
                commands_body.append(method_doc)

            commands_body.append('')
            commands_body.append('---')
            commands_body.append('')

        commands_body.append('')

    final = ['# Command Reference']

    if not omit_header:
        header_docs = inspect.getdoc(webfriend.scripting.commands)

        if header_docs:
            final.append('')
            final += header_docs.split('\n')
            final.append('')

    # include TOC tree
    for title, qualifier in toc:
        final.append("- [{}](#{}-command-set)".format(title, qualifier))

        if qualifier in subtoc:
            for method, has_docs in sorted(list(subtoc[qualifier])):
                wrap_l = wrap_r = '**'

                if not has_docs:
                    wrap_l = wrap_r = ''

                final.append("   - {}[{}](#{}){}".format(wrap_l, method, method.replace('::', ''), wrap_r))

    # include command documentation lines
    final.append('')
    final += commands_body

    return final


def get_docstring(obj):
    docstring = inspect.getdoc(obj)

    if not docstring:
        return None

    out = []
    match = RX_DOCSTRING_SEEOTHER.match(docstring.strip())

    if match:
        matches = match.groupdict()
        out = matches.get('head', '')

        if len(matches.get('module', '')):
            module, remainder = get_module_from_string(matches['module'])

            if module:
                subobj = resolve_object(remainder, parent=module)

                if subobj:
                    subdocs = inspect.getdoc(subobj)

                    if subdocs:
                        out += subdocs
                    else:
                        logging.warning('Referenced object "{}" has no documentation.'.format(
                            matches['module']
                        ))
                else:
                    logging.warning('Failed to resolve "{}" into an object'.format(
                        matches['module']
                    ))
            else:
                logging.warning('Failed to resolve "{}" into a module'.format(
                    matches['module']
                ))

        out += matches.get('tail', '')

        docstring = out

    if not len(docstring):
        return None

    return docstring


def get_signature(method):
    arguments = []
    argspec = inspect.getargspec(method[1])
    args = list(argspec.args)
    args.reverse()
    maxarglen = max([len(a) for a in args]) + 1

    if argspec.defaults:
        defaults = list(argspec.defaults)
        defaults.reverse()
    else:
        defaults = []

    for i, arg in enumerate(args):
        skip_default = False

        if arg == 'self':
            continue

        if len(defaults) and i < len(defaults):
            default = defaults[i]
        else:
            default = '<REQUIRED>'

        if len(args) == 1:
            skip_default = True
        elif i == (len(args) - 2):
            skip_default = True
        else:
            arg = (arg + ':').ljust(maxarglen)

        if not skip_default:
            wrap_l = ''
            wrap_r = ''

            if default is True:
                default = 'true'

            elif default is False:
                default = 'false'

            elif default is None:
                default = 'null'

            elif default == '<REQUIRED>':
                default

            elif isinstance(default, basestring):
                wrap_l = "'"
                wrap_r = "'"

            arg = '    {} {}{}{}'.format(arg, wrap_l, default, wrap_r)

        arguments = [arg] + arguments

    if len(arguments) == 0:
        return method[0]
    elif len(arguments) == 1:
        return '{} <{}>'.format(
            method[0],
            arguments[0].upper()
        )
    else:
        return '{} <{}> {{\n{}\n}}'.format(
            method[0],
            arguments[0].upper(),
            ',\n'.join(arguments[1:])
        )


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    print('\n'.join(document_commands()))
