import logging

from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtGui import QColor, QPen
from PySide2.QtCore import Qt, QRectF

from angrmanagement.config import Conf


_l = logging.getLogger(__name__)


class QCartBlock(QGraphicsItem):

    HORIZONTAL_PADDING = 5
    VERTICAL_PADDING = 5
    LINE_MARGIN = 3

    def __init__(self, is_selected, cartprograph_view, state=None, label=None, id=None):
        super(QCartBlock, self).__init__()

        self.cartprograph_view = cartprograph_view
        self._workspace = self.cartprograph_view.workspace

        self.state = state
        self.selected = is_selected
        self._config = Conf
        # widgets
        self.label = label
        self.label_linecount = len(self.label.split("\n"))
        self.id = id

        self.interactions = []  # dict of stuff

        self._init_widgets()
        self._update_size()

    def _init_widgets(self):
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.cartprograph_view.select_item(self.id)
            self.cartprograph_view.update_console(self.id)
            self.cartprograph_view.update_tables(self.id)
            self.cartprograph_view.redraw_graph()
            event.accept()

        super().mouseReleaseEvent(event)

    def paint(self, painter, option, widget):  # pylint: disable=unused-argument
        """
        Paint a state block on the scene.

        :param painter:
        :return: None
        """

        painter.setFont(Conf.symexec_font)
        normal_background = QColor(0xE6, 0xE6, 0xE6)  # old 0xfa
        selected_background = QColor(0xCC, 0xCC, 0xCC)

        # The node background
        if self.selected:
            painter.setBrush(selected_background)
        else:
            painter.setBrush(normal_background)
        painter.setPen(QPen(QColor(0xE1, 0xE1, 0xE1), 1.5))  # old f0
        painter.drawRect(0, 0, self.width, self.height)

        x = 0
        y = 0

        # The addr label
        label_x = x + self.HORIZONTAL_PADDING
        label_y = y + self.VERTICAL_PADDING
        painter.setPen(Qt.black)

        # multiline text support
        if "\n" in self.label:
            for i, label in enumerate(self.label.split("\n")):
                painter.drawText(
                    label_x, label_y + self._config.symexec_font_ascent * (i + 1), label
                )

        else:
            painter.drawText(
                label_x, label_y + self._config.symexec_font_ascent, self.label
            )

    @property
    def height(self):
        return self.boundingRect().height()

    @property
    def width(self):
        return self.boundingRect().width()

    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)

    #
    # Private methods
    #

    def _update_size(self):
        line_lens = []
        for line in self.label.split("\n"):
            line_lens.append(len(line))
        width_candidates = [
            self.HORIZONTAL_PADDING * 2
            + max(line_lens) * self._config.symexec_font_width
        ]
        height_candidates = [
            self.VERTICAL_PADDING * 2
            + self.label_linecount * self._config.symexec_font_ascent
        ]
        self._width = max(width_candidates)
        self._height = max(height_candidates)

        self._width = max(100, self._width)
        self._height = max(50, self._height)
