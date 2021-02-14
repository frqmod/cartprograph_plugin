from PySide2.QtGui import QPen, QColor, QBrush
from PySide2.QtCore import Qt

from angrmanagement.ui.widgets.qgraph_arrow import QGraphArrow


class QCartEdge(QGraphArrow):
    def __init__(self, edge, parent=None):
        super().__init__(edge, arrow_direction="down", parent=parent)
        self.highlighted = False

    @property
    def current_color(self):
        return QColor(230, 90, 85) if self.highlighted else QColor(0, 0, 0)

    def paint(self, painter, option, widget):
        detail = option.levelOfDetailFromTransform(painter.worldTransform())
        if detail < 0.3:
            return

        painter.setPen(QPen(self.current_color, 2, Qt.SolidLine))
        painter.drawPath(self.path)

        painter.setBrush(QBrush(self.current_color))
        painter.drawPolygon(self.arrow)
