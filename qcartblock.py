from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtGui import QColor, QPen, QFont
from PySide2.QtCore import Qt, QRectF

from angrmanagement.config import Conf


class QCartBlock(QGraphicsItem):

    HORIZONTAL_PADDING = 15
    VERTICAL_PADDING = 30
    LINE_MARGIN = 3

    def __init__(
        self,
        mouse_press_handler,
        id,
        type,
        header,
        label,
        annotation,
    ):
        super(QCartBlock, self).__init__()

        self.mouse_press_handler = mouse_press_handler

        self.id = id  # TODO: refactor this out
        self.type = type
        self.header = header
        self.label = label
        self.annotation = annotation

        self.selected = False
        self.highlighted = False

        self.addr = self.id  # Required for GraphLayouter

    @property
    def background_color(self):
        if self.type == "pending_input":
            return QColor(219, 199, 94) if self.selected else QColor(230, 219, 163)
        elif self.type == "input":
            return QColor(85, 134, 230) if self.selected else QColor(130, 157, 209)
        else:
            return QColor(204, 204, 204) if self.selected else QColor(230, 230, 230)

    @property
    def outline_color(self):
        return QColor(230, 90, 85) if self.highlighted else QColor(225, 225, 225)

    def mousePressEvent(self, event):
        self.mouse_press_handler(event)
        super().mouseReleaseEvent(event)

    def paint(self, painter, option, widget):
        painter.setBrush(self.background_color)
        painter.setPen(QPen(self.outline_color, 1.5))
        painter.drawRect(0, 0, self.width, self.height)

        x = self.HORIZONTAL_PADDING
        y = self.VERTICAL_PADDING
        painter.setPen(Qt.black)

        if self.header:
            header_font = QFont(Conf.symexec_font)
            header_font.setBold(True)
            painter.setFont(header_font)
            painter.drawText(x, y, self.header)
            painter.setFont(Conf.symexec_font)
            y += Conf.symexec_font_ascent

        painter.setFont(Conf.symexec_font)

        for line in self.label.split("\n"):
            painter.drawText(x, y, line)
            y += Conf.symexec_font_ascent

        y = self.VERTICAL_PADDING - Conf.symexec_font_ascent
        painter.setPen(Qt.darkRed)
        painter.drawText(x, y, self.annotation)

    @property
    def height(self):
        return self.boundingRect().height()

    @property
    def width(self):
        return self.boundingRect().width()

    def boundingRect(self):
        max_line_len = max(len(line) for line in self.label.split("\n"))
        num_lines = len(self.label.split("\n"))
        width = max(
            2 * self.HORIZONTAL_PADDING + max_line_len * Conf.symexec_font_width, 120
        )
        height = max(
            2 * self.VERTICAL_PADDING + num_lines * Conf.symexec_font_ascent, 50
        )
        return QRectF(0, 0, width, height)
