from __future__ import absolute_import
from webfriend.rpc import Base


class Overlay(Base):
    """
    See: https://chromedevtools.github.io/devtools-protocol/tot/Overlay
    """
    domain = 'Overlay'
    supports_events = False

    default_highlight_color = {
        'r': 0,
        'g': 99,
        'b': 193,
        'a': 0.95,
    }

    default_highlight_outline_color = {
        'r': 255,
        'g': 255,
        'b': 255,
        'a': 0,
    }

    show_rulers = False
    show_extension_lines = False
    show_info_tooltip = False

    def show_paint_rectangles(self):
        self.call('setShowPaintRects', result=True)

    def hide_paint_rectangles(self):
        self.call('setShowPaintRects', result=False)

    def show_debug_borders(self):
        self.call('setShowDebugBorders', show=True)

    def hide_debug_borders(self):
        self.call('setShowDebugBorders', show=False)

    def show_fps_counter(self):
        self.call('setShowFPSCounter', show=True)

    def hide_fps_counter(self):
        self.call('setShowFPSCounter', show=False)

    def show_scroll_bottlenecks(self):
        self.call('setShowScrollBottleneckRects', show=True)

    def hide_scroll_bottlenecks(self):
        self.call('setShowScrollBottleneckRects', show=False)

    def show_size_on_resize(self):
        self.call('setShowViewportSizeOnResize', show=True)

    def hide_size_on_resize(self):
        self.call('setShowViewportSizeOnResize', show=False)

    def suspend(self):
        self.call('setSuspended', suspended=True)

    def resume(self):
        self.call('setSuspended', suspended=False)

    def enable_inspect_mode(self):
        self.call('setInspectMode', mode='searchForNode')

    def disable_inspect_mode(self):
        self.call('setInspectMode', mode='none')

    def highlight_rect(self, x, y, width, height, color=None, outline_color=None):
        if not isinstance(color, dict):
            color = self.default_highlight_color

        if not isinstance(outline_color, dict):
            outline_color = self.default_highlight_outline_color

        self.call(
            'highlightRect',
            x=x,
            y=y,
            width=width,
            height=height,
            color=color,
            outlineColor=outline_color
        )

    def highlight_node(
        self,
        node_id=None,
        backend_node_id=None,
        object_id=None,
        show_rulers=None,
        show_extension_lines=None,
        show_info_tooltip=None,
        content_color=None,
        padding_color=None,
        border_color=None,
        margin_color=None,
        event_target_color=None,
        shape_color=None,
        shape_margin_color=None,
    ):
        params = {
            'highlightConfig': {},
        }

        if node_id:
            params['nodeId'] = node_id
        elif backend_node_id:
            params['backendNodeId'] = backend_node_id
        elif object_id:
            params['objectId'] = object_id
        else:
            raise ValueError("Must specify one of node_id or object_id")

        if not show_rulers:
            params['highlightConfig']['showRulers'] = self.show_rulers

        if not show_info_tooltip:
            params['highlightConfig']['showInfo'] = self.show_info_tooltip

        if not show_extension_lines:
            params['highlightConfig']['showExtensionLines'] = self.show_extension_lines

        if isinstance(content_color, dict):
            params['highlightConfig']['contentColor'] = content_color
        else:
            params['highlightConfig']['contentColor'] = self.default_highlight_color

        if isinstance(padding_color, dict):
            params['highlightConfig']['paddingColor'] = padding_color

        if isinstance(border_color, dict):
            params['highlightConfig']['borderColor'] = border_color

        if isinstance(margin_color, dict):
            params['highlightConfig']['marginColor'] = margin_color

        if isinstance(event_target_color, dict):
            params['highlightConfig']['eventTargetColor'] = event_target_color

        if isinstance(shape_color, dict):
            params['highlightConfig']['shapeColor'] = shape_color

        if isinstance(shape_margin_color, dict):
            params['highlightConfig']['shapeMarginColor'] = shape_margin_color

        self.call('highlightNode', **params)

    def hide_highlight(self):
        self.call('hideHighlight')
