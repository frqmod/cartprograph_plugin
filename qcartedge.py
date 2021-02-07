from PySide2.QtGui import QPen, QColor, QBrush
from PySide2.QtCore import Qt
from angrmanagement.ui.widgets.qgraph_arrow import QGraphArrow


class QCartEdge(QGraphArrow):
    def __init__(self, edge, cartprograph_view, parent=None):
        super().__init__(edge, arrow_direction="down", parent=parent)
        self.cartprograph_view = cartprograph_view
        self.color = QColor(0, 0, 0)  # black by default
        self.highlighted_color = QColor(230, 90, 85)
        self.style = Qt.SolidLine
        self.highlighted = False

    def mousePressEvent(self, event):
        # if event.button() == Qt.LeftButton:
        #     self.cartprograph_view.select_item((self.edge.src.id, self.edge.dst.id))
        #     self.cartprograph_view.update_console(self.edge.src.id)
        #     self.cartprograph_view.update_tables(self.edge.src.id)
        #     self.cartprograph_view.redraw_graph()
        #     event.accept()

        super().mouseReleaseEvent(event)

    def paint(self, painter, option, widget):
        lod = option.levelOfDetailFromTransform(painter.worldTransform())
        if self.highlighted:
            pen = QPen(self.highlighted_color, 2, self.style)
        else:
            pen = QPen(self.color, 2, self.style)
        painter.setPen(pen)
        painter.drawPath(self.path)

        # arrow
        if lod < 0.3:
            return

        if self.highlighted:
            brush = QBrush(self.highlighted_color)
        else:
            brush = QBrush(self.color)
        painter.setBrush(brush)
        painter.drawPolygon(self.arrow)
