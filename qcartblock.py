import logging

from PySide2.QtWidgets import QGraphicsItem, QInputDialog, QLineEdit
from PySide2.QtGui import QColor, QPen
from PySide2.QtCore import Qt, QRectF

from angrmanagement.config import Conf


_l = logging.getLogger(__name__)


class QCartBlock(QGraphicsItem):

    HORIZONTAL_PADDING = 15
    VERTICAL_PADDING = 15
    LINE_MARGIN = 3

    def __init__(
        self,
        is_selected,
        cartprograph_view,
        state=None,
        label=None,
        id=None,
        type=None,
        annotation="",
        header=None,
    ):
        super(QCartBlock, self).__init__()

        self.cartprograph_view = cartprograph_view
        self._workspace = self.cartprograph_view.workspace

        self.state = state
        self.selected = is_selected
        self.highlighted = False
        self._config = Conf
        # widgets
        self.label = label
        self.label_linecount = len(self.label.split("\n"))
        self.header = header
        self.hasHeader = True if self.header is not None else False
        self.id = id
        self.annotation = annotation

        self.type = type
        self.normal_background = QColor(0xE6, 0xE6, 0xE6)  # old 0xfa
        self.selected_background = QColor(0xCC, 0xCC, 0xCC)
        self.pend_input_background = QColor(230, 219, 163)
        self.pend_selected_input_background = QColor(219, 199, 94)
        self.input_background = QColor(130, 157, 209)
        self.selected_input_background = QColor(85, 134, 230)

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

        if event.button() == Qt.RightButton:
            annotation_dialog = QInputDialog()
            annotation_dialog.setInputMode(QInputDialog.TextInput)
            annotation_dialog.setLabelText("Annotation:")
            annotation_dialog.resize(400, 100)
            ok = annotation_dialog.exec_()
            result = annotation_dialog.textValue()

            if ok:
                self.annotation = result
                self.cartprograph_view.store_annotation(self.id, self.annotation)
                self.cartprograph_view.redraw_graph()

        if event.button() == Qt.MiddleButton:
            self.cartprograph_view.update_graph(self.cartprograph_view.G)
            return

        super().mouseReleaseEvent(event)

    def paint(self, painter, option, widget):  # pylint: disable=unused-argument
        """
        Paint a state block on the scene.

        :param painter:
        :return: None
        """

        painter.setFont(Conf.symexec_font)

        # The node background
        if self.type == "pending_input":
            if self.selected:
                painter.setBrush(self.pend_selected_input_background)
            else:
                painter.setBrush(self.pend_input_background)
        elif self.type == "input":
            if self.selected:
                painter.setBrush(self.selected_input_background)
            else:
                painter.setBrush(self.input_background)
        else:
            if self.selected:
                painter.setBrush(self.selected_background)
            else:
                painter.setBrush(self.normal_background)

        if self.highlighted:
            painter.setPen(QPen(QColor(230, 90, 85), 1.5))
        else:
            painter.setPen(QPen(QColor(0xE1, 0xE1, 0xE1), 1.5))
        painter.drawRect(0, 0, self.width, self.height)

        x = 0
        y = 0

        # The addr label
        label_x = x + self.HORIZONTAL_PADDING
        label_y = y + self.VERTICAL_PADDING
        painter.setPen(Qt.black)

        spacing = 1
        if self.hasHeader:
            Conf.symexec_font.setBold(True)
            painter.setFont(Conf.symexec_font)
            painter.drawText(
                label_x, label_y + self._config.symexec_font_ascent, self.header
            )
            spacing += 1
            Conf.symexec_font.setBold(False)
            painter.setFont(Conf.symexec_font)

        # multiline text support
        if "\n" in self.label:
            for i, label in enumerate(self.label.split("\n")):
                painter.drawText(
                    label_x,
                    label_y + self._config.symexec_font_ascent * (i + spacing),
                    label,
                )

        else:
            painter.drawText(
                label_x,
                label_y + self._config.symexec_font_ascent * spacing,
                self.label,
            )

        painter.setPen(Qt.darkRed)
        # draw user_label
        painter.drawText(
            label_x, label_y - self._config.symexec_font_ascent * 0.5, self.annotation
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
        self._height = max(height_candidates) + self.VERTICAL_PADDING

        self._width = max(120, self._width)
        self._height = max(50, self._height)
