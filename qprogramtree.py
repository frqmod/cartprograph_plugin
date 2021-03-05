from PySide2.QtCore import Qt, QPointF, QRectF

from angrmanagement.ui.widgets.qgraph import QZoomableDraggableGraphicsView
from angrmanagement.utils.graph_layouter import GraphLayouter

from .qcartedge import QCartEdge


class QProgramTree(QZoomableDraggableGraphicsView):

    LEFT_PADDING = 2000
    TOP_PADDING = 2000

    def __init__(self, workspace, parent=None):
        super(QProgramTree, self).__init__(parent=parent)

        # TODO: whatever requires this to have access to the workspace is wrong
        self.workspace = workspace
        self._graph = None

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, value):
        if value is not self._graph:
            self._graph = value
            self.reload()

    def reload(self):
        self._reset_scene()

        if self.graph is None:
            return

        node_sizes = {node: (node.width, node.height) for node in self.graph.nodes()}
        layout = GraphLayouter(self.graph, node_sizes)

        scene = self.scene()

        for edge in layout.edges:
            arrow = QCartEdge(edge)
            self.workspace.cartprograph.edges[(edge.src.id, edge.dst.id)] = arrow
            arrow.setPos(QPointF(*edge.coordinates[0]))
            scene.addItem(arrow)

        for node, (x, y) in layout.node_coordinates.items():
            node.setPos(x, y)
            scene.addItem(node)

        rect = scene.itemsBoundingRect()
        scene.setSceneRect(
            QRectF(
                rect.x() - 200,
                rect.y() - 200,
                rect.width() + 400,
                rect.height() + 400,
            )
        )

    def _initial_position(self):
        ibr = self.scene().itemsBoundingRect()
        return ibr.center()
