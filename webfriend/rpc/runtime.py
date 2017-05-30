from __future__ import absolute_import
from . import Base
from uuid import uuid4
import inspect
import os.path
from .. import utils


class ScriptError(Exception):
    pass


class Runtime(Base):
    domain = 'Runtime'
    enable_events = False

    def evaluate(self, expression, return_by_value=True, wrapper_fn=True):
        if wrapper_fn:
            fn_name = 'eval_{}_fn'.format(str(uuid4()).replace('-', '_'))
            expression = 'var {} = function(){{ {} }}; {}()'.format(
                fn_name,
                expression,
                fn_name
            )

        reply = self.call(
            'evaluate',
            expression=expression,
            returnByValue=return_by_value
        )

        if 'exceptionDetails' in reply.result:
            exception = reply.result['exceptionDetails']
            detail    = exception.get('exception', {})
            stack = inspect.stack()[1]
            common_prefix = os.path.commonprefix([
                utils.PACKAGE_ROOT,
                stack[1],
            ])

            calling_file = stack[1][len(common_prefix):].lstrip('/')

            # provide LOTS of context from both where the injected script failed AND where
            # the script was injected from in our local call stack.
            raise ScriptError('{} on line {}; called from {}/{}:{}'.format(
                detail.get(
                    'description',
                    detail.get(
                        'value',
                        exception.get(
                            'text',
                            'Unknown Error'
                        )
                    )
                ),
                exception['lineNumber'],
                utils.PACKAGE_NAME,
                calling_file,
                stack[2]
            ))

        else:
            return reply.result.get('result', {}).get('value')

    def call_function_on(self, object_id, fn_name, arguments=None, return_by_value=False):
        return self.call(
            'callFunctionOn',
            objectId=object_id,
            functionDeclaration=fn_name,
            arguments=[{
                'value': v,
            } for v in (arguments or [])],
            returnByValue=return_by_value
        )

    def get_properties(self, object_id, own_properties=False, accessors_only=False, preview=False):
        params = {
            'objectId': object_id,
        }

        if own_properties:
            params['ownProperties'] = True

        if accessors_only:
            params['accessorPropertiesOnly'] = True

        if preview:
            params['generatePreview'] = True

        return self.call('getProperties', **params)

    def release_object(self, object_id):
        self.call('releaseObject', objectId=object_id)

    def release_object_group(self, object_group):
        self.call('releaseObjectGroup', objectGroup=object_group)
