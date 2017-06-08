from __future__ import absolute_import
import inspect
from webfriend.scripting import commands


def document_commands():
    base = commands.base.CommandProxy
    toc = []
    subtoc = {}
    commands_body = []
    classes = []

    for cls in inspect.getmembers(commands, inspect.isclass):
        if issubclass(cls[1], base):
            if cls[1] is not base:
                classes.append(cls)

    classes = [
        c for c in classes if c[0] == 'CoreProxy'
    ] + sorted([
        c for c in classes if c[0] != 'CoreProxy'
    ])

    for cls in classes:
        proxy = cls[1]
        proxy_docs = inspect.getdoc(proxy)
        commands_body.append("## `{}` Command Set".format(proxy.as_qualifier()))
        commands_body.append('')

        tocentry = (proxy.as_qualifier().title(), proxy.as_qualifier())

        if tocentry not in toc:
            toc.append(tocentry)

        subtoc[proxy.as_qualifier()] = set()

        if proxy_docs:
            commands_body.append(proxy_docs)

        for method in inspect.getmembers(proxy, inspect.ismethod):
            if method[0].startswith('_'):
                continue

            if method[0] in dir(base):
                continue

            method_doc = inspect.getdoc(method[1])

            commands_body.append("### `{}`".format(proxy.qualify(method[0])))
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

        commands_body.append('')

    print('## Command Reference')

    for title, qualifier in toc:
        print("- [{}](#{}-command-set)".format(title, qualifier))

        if qualifier in subtoc:
            for method, has_docs in sorted(list(subtoc[qualifier])):
                wrap_l = wrap_r = '**'

                if not has_docs:
                    wrap_l = wrap_r = ''

                print("   - {}[{}](#{}){}".format(wrap_l, method, method.replace('::', ''), wrap_r))

    print('')

    print('\n'.join(commands_body))


def get_signature(method):
    arguments = []
    argspec = inspect.getargspec(method[1])
    args = list(argspec.args)
    args.reverse()

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

        if len(args) == 1:
            skip_default = True
        elif i == (len(args) - 2):
            skip_default = True
        else:
            default = None

        if not skip_default:
            wrap_l = ''
            wrap_r = ''

            if default is True:
                default = 'true'
            elif default is False:
                default = 'false'
            elif default is None:
                default = 'null'

            if isinstance(default, basestring):
                wrap_l = "'"
                wrap_r = "'"

            arg = '    {}: {}{}{}'.format(arg, wrap_l, default, wrap_r)

        arguments = [arg] + arguments

    if len(arguments) == 0:
        return method[0]
    elif len(arguments) == 1:
        return '{} _{}_'.format(method[0], arguments[0])
    else:
        return '{} _{}_ {{\n{}\n}}'.format(method[0], arguments[0], ',\n'.join(arguments[1:]))


if __name__ == '__main__':
    document_commands()
