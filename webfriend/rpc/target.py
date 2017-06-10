from __future__ import absolute_import
from webfriend.rpc import Base


class Target(Base):
    """
    See: https://chromedevtools.github.io/devtools-protocol/tot/Target
    """
    domain = 'Target'
    supports_events = False

    def enable_auto_attach(self, wait_for_debugger=True):
        self.call('setAutoAttach', autoAttach=True, waitForDebuggerOnStart=wait_for_debugger)

    def disable_auto_attach(self):
        self.call('setAutoAttach', autoAttach=False)

    def enable_discover_targets(self):
        self.call('setDiscoverTargets', discover=True)

    def disable_discover_targets(self):
        self.call('setDiscoverTargets', discover=False)

    def enable_attach_to_frames(self):
        self.call('setAttachToFrames', value=True)

    def disable_attach_to_frames(self):
        self.call('setAttachToFrames', value=False)

    def send_message_to_target(self, target_id, message):
        self.call('sendMessageToTarget', targetId=target_id, message=message)

    def get_targets(self):
        return self.call('getTargets')

    def get_target_info(self, target_id):
        return self.call('getTargetInfo', targetId=target_id)

    def create_target(self, url, width=None, height=None, browser_context_id=None):
        params = {
            'url': url,
        }

        if width:
            params['width'] = width

        if height:
            params['height'] = height

        if browser_context_id:
            params['browserContextId'] = browser_context_id

        return self.call('createTarget', **params)

    def activate_target(self, target_id):
        self.call('activateTarget', targetId=target_id)

    def close_target(self, target_id):
        self.call('closeTarget', targetId=target_id)

    def attach_to_target(self, target_id):
        return self.call_boolean_response('attachToTarget', field='success', targetId=target_id)

    def detach_from_target(self, target_id):
        self.call('detachFromTarget', targetId=target_id)

    def create_browser_context(self):
        return self.call('createBrowserContext')

    def dispose_browser_context(self, browser_context_id):
        return self.call_boolean_response(
            'disposeBrowserContext',
            field='success',
            browserContextId=browser_context_id
        )
