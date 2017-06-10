from __future__ import absolute_import
from webfriend.rpc import Base
import time
from random import random


class Input(Base):
    """
    See: https://chromedevtools.github.io/devtools-protocol/tot/Input
    """

    domain = 'Input'
    supports_events = False
    key_event_types = ['keyDown', 'keyUp', 'rawKeyDown', 'char']
    key_events_with_text = ['keyDown', 'char']
    key_args = [
        ('timestamp', 'timestamp'),
        ('unmodified_text', 'unmodifiedText'),
        ('key_identifier', 'keyIdentifier'),
        ('code', 'code'),
        ('dom_key', 'key'),
        ('windows_virtual_keycode', 'windowsVirtualKeyCode'),
        ('native_virtual_keycode', 'nativeVirtualKeyCode'),
        ('is_autorepeat', 'autoRepeat'),
        ('is_keypad', 'isKeypad'),
        ('is_system', 'isSystemKey'),
    ]

    mouse_event_types = ['mousePressed', 'mouseReleased', 'mouseMoved']
    mouse_buttons = ['left', 'middle', 'right']

    def ignore_input(self):
        self.call('setIgnoreInputEvents', ignore=True)

    def accept_input(self):
        self.call('setIgnoreInputEvents', ignore=False)

    def dispatch_key_event(
        self,
        event_type='keyDown',
        alt=False,
        control=False,
        meta=False,
        shift=False,
        timestamp=None,
        text=None,
        unmodified_text=None,
        key_identifier=None,
        code=None,
        dom_key=None,
        windows_virtual_keycode=None,
        native_virtual_keycode=None,
        is_autorepeat=False,
        is_keypad=False,
        is_system=False
    ):
        """
        See: https://chromedevtools.github.io/devtools-protocol/tot/Input/#method-dispatchKeyEvent
        """
        params = {
            'type':      event_type,
            'modifiers': 0,
        }

        if event_type not in self.key_event_types:
            raise ValueError("event_type must be one of: {}".format(
                ', '.join(self.key_event_types)
            ))

        if event_type in self.key_events_with_text:
            if text is None:
                raise ValueError("text must be specified for '{}' event".format(event_type))
            else:
                params['text'] = text

        params['modifiers'] |= 1 if alt else 0
        params['modifiers'] |= 2 if control else 0
        params['modifiers'] |= 4 if meta else 0
        params['modifiers'] |= 8 if shift else 0

        for local, param_name in self.key_args:
            if locals()[local]:
                params[param_name] = locals()[local]

        self.call('dispatchKeyEvent', **params)

    def type_text(
        self,
        text,
        file=False,
        alt=False,
        control=False,
        meta=False,
        shift=False,
        is_keypad=False,
        key_down_time=30,
        key_down_jitter=0,
        delay=50,
        delay_jitter=0
    ):
        """
        Input the given textual data as keyboard input into the browser in its current state.

        #### Arguments

        - **text** (`str`, optional):

            The text string to input, one character or symbol at a time.

        - **file** (`str`, optional):

            If specified, read the text to input from the named file.

        - **alt**, **control**, **meta**, **shift** (`bool`):

            Declares that the Alt, Control, Meta/Command, and/or Shift keys (respectively) are
            depressed at the time of the click action.

        - **is_keypad** (`bool`, optional):

            Whether the text being input is issued via the numeric keypad or not.

        - **key_down_time** (`int`, optional):

            How long, in milliseconds, that each individual keystroke will remain down for.

        - **key_down_jitter** (`int`, optional):

            An amount of time, in milliseconds, to randomly vary the **key_down_time** duration
            from within each keystroke.

        - **delay** (`int`, optional):

            How long, in milliseconds, to wait between issuing individual keystrokes.

        - **delay_jitter** (`int`, optional):

            An amount of time, in milliseconds, to randomly vary the **delay** duration
            from between keystrokes.

        #### Returns
        The text that was submitted.
        """
        if file:
            text = open(text, 'r').read()
        elif text is None:
            raise ValueError("Must specify either 'text' or 'file' to read input from.")

        for char in text:
            self.dispatch_key_event(
                event_type='keyDown',
                text=char,
                alt=alt,
                control=control,
                meta=meta,
                shift=shift,
                is_keypad=is_keypad
            )

            # simulate the duration of the keypress
            if key_down_time:
                time.sleep((key_down_time * key_down_jitter * random()) / 1e3)

            # send the keyUp event
            self.dispatch_key_event(event_type='keyUp')

            # simulate the time between key presses
            if delay:
                time.sleep((delay * random() * delay_jitter) / 1e3)

        return text

    def dispatch_mouse_event(
        self,
        x,
        y,
        event_type='mouseMoved',
        button=None,
        alt=False,
        control=False,
        meta=False,
        shift=False,
        timestamp=None,
        click_count=1,
    ):
        """
        See https://chromedevtools.github.io/devtools-protocol/tot/Input/#method-dispatchMouseEvent
        """
        params = {
            'type':      event_type,
            'x':         int(x),
            'y':         int(y),
            'modifiers': 0,
        }

        if event_type not in self.mouse_event_types:
            raise ValueError("event_type must be one of: {}".format(
                ', '.join(self.mouse_event_types)
            ))

        if button and button not in self.mouse_buttons:
            raise ValueError("button must be one of: {}".format(
                ', '.join(self.mouse_buttons)
            ))

        params['modifiers'] |= 1 if alt else 0
        params['modifiers'] |= 2 if control else 0
        params['modifiers'] |= 4 if meta else 0
        params['modifiers'] |= 8 if shift else 0

        if timestamp:
            params['timestamp'] = timestamp

        if button:
            params['button'] = button

        if click_count:
            params['clickCount'] = click_count

        self.call('dispatchMouseEvent', **params)

    def click_at(
        self,
        x,
        y,
        button='left',
        alt=False,
        control=False,
        meta=False,
        shift=False,
        move_to=True,
        drag=False,
        start_x=None,
        start_y=None,
        drag_start_delay=50,
        move_finish_delay=50,
        click_duration=50
    ):
        """
        Dispatch low-level mouse events at the given coordinates to perform a variety of actions.

        #### Arguments

        - **x**, **y** (`int`):

            The X- and Y-coordinates describing the click location.

        **button** (`str`):

            Which mouse button the event will be for; one of: `left`, `middle`, or `right`.

        **alt**, **control**, **meta**, **shift** (`bool`):

            Declares that the Alt, Control, Meta/Command, and/or Shift keys (respectively) are
            depressed at the time of the click action.

        **move_to** (`bool`):

            Simulates the mouse moving from the starting location to the destination **x**/**y**
            coordinates.

        **drag** (`bool`):

            If specified, the click operation will be a "drag and drop" style movement, wherein
            a set of initial coordinates receive a mouse press, then (with the button still
            pressed) the mouse will move to the destination coordinates, and _then_ the button
            release event will fire.

        **start_x** (`int`):

            For **drag** operations, the starting X-coordinate.

        **start_y** (`int`):

            For **drag** operations, the starting Y-coordinate.

        **drag_start_delay** (`int`):

            For **drag** operations, how long to wait (in milliseconds) after the initial mouse
            button press before starting to move.

        **move_finish_delay** (`int`):

            If simulating mouse movement with **move_to**, how long to wait (in milliseconds)
            _after_ the move is completed, but before clicking or releasing.

        **click_duration** (`int`):

            If non-zero and not dragging, how long (in milliseconds) the mouse button should be
            held for when  performing the click; i.e.: how long between the mouse press and mouse
            release events.
        """

        is_dragging = False

        # dragging entails pressing the mouse, moving it, then releasing it
        if drag:
            if start_x is not None and start_y is not None:
                self.dispatch_mouse_event(
                    start_x,
                    start_y,
                    event_type='mousePressed',
                    button=button,
                    alt=alt,
                    control=control,
                    meta=meta,
                    shift=shift,
                )

                is_dragging = True
                time.sleep(drag_start_delay / 1e3)

            else:
                raise AttributeError("If drag is specified, start_x and start_y must be given as well")

        # move the mouse, optionally with a button pressed if we're dragging
        if move_to:
            self.dispatch_mouse_event(
                x,
                y,
                event_type='mouseMoved',
                button=(button if is_dragging else None),
                alt=alt,
                control=control,
                meta=meta,
                shift=shift,
            )

            time.sleep(move_finish_delay / 1e3)

        # if we're dragging, then release the button now that we're where we're going
        if is_dragging:
            self.dispatch_mouse_event(
                x,
                y,
                event_type='mouseReleased',
                button=button,
                alt=alt,
                control=control,
                meta=meta,
                shift=shift,
            )

            is_dragging = False
        else:
            # otherwise, click the button
            self.dispatch_mouse_event(
                x,
                y,
                event_type='mousePressed',
                button=button,
                alt=alt,
                control=control,
                meta=meta,
                shift=shift,
            )

            if click_duration:
                # hold it.....
                time.sleep(click_duration / 1e3)

            # and release
            self.dispatch_mouse_event(
                x,
                y,
                event_type='mouseReleased',
                button=button,
                alt=alt,
                control=control,
                meta=meta,
                shift=shift,
            )
