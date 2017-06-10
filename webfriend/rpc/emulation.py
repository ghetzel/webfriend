from __future__ import absolute_import
from webfriend.rpc import Base
import math


class Emulation(Base):
    """
    See: https://chromedevtools.github.io/devtools-protocol/tot/Emulation
    """
    domain = 'Emulation'
    supports_events = False

    valid_orientations = [
        'portraitPrimary',
        'portraitSecondary',
        'landscapePrimary',
        'landscapeSecondary',
    ]

    def set_device_metrics_override(
        self,
        width=0,
        height=0,
        device_scale_factor=0,
        mobile=False,
        fit_window=False,
        mobile_screen_width=0,
        mobile_screen_height=0,
        mobile_position_x=0,
        mobile_position_y=0,
        screen_orientation_type=None,
        screen_orientation_angle=None
    ):
        params = {
            'width':             int(math.ceil(width)),
            'height':            int(math.ceil(height)),
            'deviceScaleFactor': device_scale_factor,
            'mobile':            mobile,
            'fitWindow':         fit_window,
        }

        if mobile is True:
            params['screenWidth']  = mobile_screen_width
            params['screenHeight'] = mobile_screen_height
            params['positionX']    = mobile_position_x
            params['positionY']    = mobile_position_y

        if screen_orientation_type is not None:
            params['screenOrientation'] = {
                'type':  screen_orientation_type,
                'angle': (screen_orientation_angle or 0),
            }

        self.call('setDeviceMetricsOverride', **params)

    def clear_device_metrics_override(self):
        self.call('clearDeviceMetricsOverride')

    def force_viewport(self, x=0, y=0, scale=1.0):
        self.call('forceViewport', x=x, y=y, scale=scale)

    def reset_viewport(self):
        self.call('resetViewport')

    def set_page_scale_factor(self, factor):
        self.call('setPageScaleFactor', pageScaleFactor=factor)

    def reset_page_scale_factor(self):
        self.call('resetPageScaleFactor')

    def set_visible_size(self, width, height):
        self.call(
            'setVisibleSize',
            width=int(math.ceil(width)),
            height=int(math.ceil(height))
        )

    def enable_script_execution(self):
        self.call('setScriptExecutionDisabled', value=False)

    def disable_script_execution(self):
        self.call('setScriptExecutionDisabled', value=True)

    def set_geolocation_override(self, latitude, longitude, accuracy):
        self.call(
            'setGeolocationOverride',
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy
        )

    def clear_geolocation_override(self):
        self.call('clearGeolocationOverride')

    def enable_touch_emulation(self, configuration=None):
        params = {
            'enabled': True,
        }

        if configuration is not None:
            params['configuration'] = configuration

        self.call('setTouchEmulationEnabled', **params)

    def set_emulated_media(self, media):
        self.call('setEmulatedMedia', media=media)

    def set_cpu_throttling_rate(self, rate):
        self.call('setCPUThrottlingRate', rate=rate)

    def can_emulate(self):
        return self.call_boolean_response('canEmulate')

    def set_default_background_color_override(self, red, green, blue, alpha=1.0):
        self.call('setDefaultBackgroundColorOverride', color={
            'r': red,
            'g': green,
            'b': blue,
            'a': alpha,
        })

    def clear_default_background_color_override(self):
        self.call('setDefaultBackgroundColorOverride')
