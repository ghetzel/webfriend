from __future__ import absolute_import
from webfriend.rpc import Base
from webfriend import exceptions, utils
from base64 import b64decode
import os
import time
import logging


class Page(Base):
    """
    See: https://chromedevtools.github.io/devtools-protocol/tot/Page
    """
    domain = 'Page'
    capture_formats = ['jpeg', 'png']

    def navigate(self, url, referrer=None, transition_type=None):
        params = {
            'url': url,
        }

        if referrer:
            params['referrer'] = referrer

        if transition_type:
            params['transitionType'] = transition_type

        self.call('navigate', **params)
        events = self.tab.wait_for('Network.responseReceived')

        net_event = events['sequence'][0]
        response = net_event.get('response', {})
        status = response['status']

        if status < 400:
            return response
        else:
            exc = exceptions.HttpError('HTTP {}'.format(status))
            exc.response = response
            raise exc

    def reload(self, ignore_cache=False, eval_on_load=None):
        params = {
            'ignoreCache': ignore_cache,
        }

        if isinstance(eval_on_load, basestring):
            params['scriptToEvaluateOnLoad'] = eval_on_load

        self.call('reload', **params)

    def stop(self):
        self.call('stopLoading')

    def dialog(self, accept, text=None):
        params = {
            'accept': accept,
        }

        if isinstance(text, basestring):
            params['promptText'] = text

        self.call('handleJavaScriptDialog', **params)

    def capture_screenshot(self, destination, format=None, quality=None, from_surface=True):
        params = {}

        if format is not None:
            if format in self.capture_formats:
                params['format'] = format
            else:
                raise AttributeError("Invalid format, must be one of: {}".format(
                    ', '.join(self.capture_formats)
                ))

        if format == 'jpeg' and isinstance(quality, int):
            params['quality'] = quality

        if from_surface is False:
            params['fromSurface'] = False

        reply = self.call('captureScreenshot', **params)

        if isinstance(destination, basestring):
            data = open(destination, 'w')

        body = b64decode(reply.get('data'))
        data.write(body)

        return len(body)

    def start_screencast(
        self,
        format='png',
        jpeg_quality=85,
        max_width=None,
        max_height=None,
        every_nth=None,
        duration=None,
        destination=None,
        filename_format=None,
        additional_values=None
    ):
        if hasattr(self, '_active_screencast'):
            if self._active_screencast:
                raise Exception("There is already an active screencast session running.")
        else:
            self._active_screencast = None

        if not filename_format:
            filename_format = '{page_id}_{screencast_id}_{frame_number}.{extension}'

        params = {
            'format': format,
        }

        if not additional_values:
            additional_values = {}

        if format == 'png':
            additional_values['extension'] = 'png'
        elif format == 'jpeg':
            additional_values['extension'] = 'jpg'

            if jpeg_quality:
                params['quality'] = jpeg_quality

        if max_width:
            params['maxWidth'] = max_width

        if max_height:
            params['maxHeight'] = max_height

        if every_nth:
            params['everyNthFrame'] = every_nth

        if destination:
            abs_dir = os.path.abspath(destination)

            if not os.path.isdir(abs_dir):
                os.makedirs(abs_dir)

            # generate the frame handler function for this screencast
            handler = self.get_receive_screencast_frame_handler(
                utils.random_string(8),
                abs_dir,
                filename_format,
                **{
                    'duration':                 duration,
                    'poll_interval_multiplier': (every_nth or 1),
                    'extra':                    additional_values,
                }
            )

            # register the event handler
            self._active_screencast = self.on('screencastFrame', handler)

        # start the screencast
        self.call('startScreencast', **params)

        # wait for the screencast to start before returning
        self.tab.wait_for('Page.screencastVisibilityChanged')

        # note the time
        self._active_screencast_started_at = time.time()

        return {
            'started_at': self._active_screencast_started_at,
            'handler_id': self._active_screencast,
        }

    def get_receive_screencast_frame_handler(
        self,
        screencast_id,
        destination,
        filename_format,
        started_at=None,
        duration=None,
        poll_interval_multiplier=1,
        extra=None
    ):
        self._active_screencast_frame_count = 0

        def handle(frame):
            frame_session_id = frame.get('sessionId')

            filename = filename_format.format(**{
                'page_id':       self.tab.frame_id.replace('-', ''),
                'screencast_id': str(screencast_id),
                'frame_number':  self._active_screencast_frame_count,
                'metadata':      frame.get('metadata'),
                'extension':     extra.get('extension'),
                'extra':         (extra if isinstance(extra, dict) else {}),
            })

            # write the data out to the file
            with open(os.path.join(destination, filename), 'w') as file:
                data = frame.get('data')

                if data and len(data):
                    file.write(b64decode(data))

            # acknowledge the frame
            self.screencast_frame_ack(frame_session_id)
            logging.debug('Wrote frame {} to {}'.format(self._active_screencast_frame_count, filename))

            self._active_screencast_frame_count += 1

            # if we only want to screencast for a specific duration, check the
            # times and stop if necessary
            if duration:
                if hasattr(self, '_active_screencast_started_at'):
                    if time.time() > (self._active_screencast_started_at + (duration / 1e3)):
                        self.stop_screencast()

        return handle

    def stop_screencast(self, timeout=10000):
        if self._active_screencast:
            logging.debug('Stopping screencast {}'.format(self._active_screencast))
            self.remove_handler(self._active_screencast)
            self._active_screencast = None

        self.call('stopScreencast')
        return True

    def screencast_frame_ack(self, session_id):
        self.call('screencastFrameAck', sessionId=session_id)
        return True

    # addScriptToEvaluateOnLoad[ scriptSource=string ]
    #   -> string(identifier)
    #
    # removeScriptToEvaluateOnLoad
    #   -> string(identifier)
    #
    # setAutoAttachToCreatedPages [ autoAttach=bool ] -> Nothing
    #
    # getNavigationHistory
    #   -> integer(currentIndex)
    #   -> []entries
    #      @NavigationEntry
    #       id=integer           Unique id of the navigation history entry.
    #       url=string           URL of the navigation history entry.
    #       userTypedURL=string  URL that the user typed in the url bar.
    #       title=string         Title of the navigation history entry.
    #       transitionType=(
    #           link,
    #           typed,
    #           auto_bookmark,
    #           auto_subframe,
    #           manual_subframe,
    #           generated,
    #           auto_toplevel,
    #           form_submit,
    #           reload,
    #           keyword,
    #           keyword_generated,
    #           other
    #       )
    #
    # navigateToHistoryEntry [ entryId=integer ]
    #
    # getResourceTree
    # getResourceContent
    # searchInResource
    #
    # setDocumentContent [ frameId=string html=string ]
