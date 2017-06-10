from __future__ import absolute_import
from webfriend.rpc import Base
from uuid import uuid4
import json


class EmbeddedScriptError(Exception):
    def __init__(self, message, line=None, col=None, **kwargs):
        self.line = line
        self.col = col
        super(Exception, self).__init__(message, **kwargs)


class Runtime(Base):
    """
    See: https://chromedevtools.github.io/devtools-protocol/tot/Runtime
    """
    domain = 'Runtime'
    supports_events = False

    def evaluate(
        self,
        expression,
        object_group=None,
        include_command_line_api=True,
        silent=None,
        context_id=None,
        return_by_value=True,
        generate_preview=None,
        user_gesture=None,
        await_promise=None,
        obj_own_properties=True,
        obj_accessors_only=False,
        obj_preview=False,
        wrapper_fn=True,
        data=None,
        calling_context=None
    ):
        if isinstance(data, dict):
            preamble = 'var webfriend = {};'.format(json.dumps(data))
            expression = preamble + expression

        if wrapper_fn:
            fn_name = 'eval_{}_fn'.format(str(uuid4()).replace('-', '_'))
            expression = 'var {} = function(){{ {} }}; {}()'.format(
                fn_name,
                expression,
                fn_name
            )

        params = {
            'expression':    expression,
            'returnByValue': return_by_value,
        }

        if object_group is not None:
            params['objectGroup'] = object_group

        if include_command_line_api is not None:
            params['includeCommandLineAPI'] = include_command_line_api

        if silent is not None:
            params['silent'] = silent

        if context_id is not None:
            params['contextId'] = context_id

        if generate_preview is not None:
            params['generatePreview'] = generate_preview

        if user_gesture is not None:
            params['userGesture'] = user_gesture

        if await_promise is not None:
            params['awaitPromise'] = await_promise

        reply = self.call('evaluate', **params)

        if 'exceptionDetails' in reply.result:
            exception   = reply.result['exceptionDetails']
            detail      = exception.get('exception', {})
            line_number = exception['lineNumber'] + 1
            col_number  = exception['columnNumber'] + 1  # add 1 because javascript columns are zero-based, we're not

            if calling_context:
                if hasattr(calling_context, 'line'):
                    line_number += calling_context.line

            # provide LOTS of context from both where the injected script failed AND where
            # the script was injected from in our local call stack.
            raise EmbeddedScriptError('{}'.format(
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
                line_number
            ), line=line_number, col=col_number)

        else:
            result = reply.result.get('result', {})

            if return_by_value:
                return result.get('value')
            elif 'objectId' in result:
                return self.get_properties(
                    result['objectId'],
                    own_properties=obj_own_properties,
                    accessors_only=obj_accessors_only,
                    preview=obj_preview
                )
            else:
                return None

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

    def get_properties(
        self,
        object_id,
        own_properties=False,
        accessors_only=False,
        preview=False
    ):
        params = {
            'objectId': object_id,
        }

        if own_properties:
            params['ownProperties'] = True

        if accessors_only:
            params['accessorPropertiesOnly'] = True

        if preview:
            params['generatePreview'] = True

        return self.call('getProperties', **params).get('result')

    def release_object(self, object_id):
        self.call('releaseObject', objectId=object_id)

    def release_object_group(self, object_group):
        self.call('releaseObjectGroup', objectGroup=object_group)
