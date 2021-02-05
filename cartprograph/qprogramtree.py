import logging

from PySide2.QtGui import QColor, QPen, QBrush, QPainter
from PySide2.QtCore import Qt, QPointF

from .cartgraphlayouter import CartGraphLayouter
from .qcartedge import QCartEdge
from ...ui.widgets.qgraph import QZoomableDraggableGraphicsView
from ...ui.widgets.qgraph_arrow import QDisasmGraphArrow
from ...utils.graph_layouter import GraphLayouter


l = logging.getLogger("ui.widgets.qpg_graph")


class QProgramTree(QZoomableDraggableGraphicsView):

    LEFT_PADDING = 2000
    TOP_PADDING = 2000

    def __init__(self, workspace, cartprograph_view, parent=None):
        super(QProgramTree, self).__init__(parent=parent)

        self.cartprograph_view = cartprograph_view
        self.workspace = workspace
        self._graph = None
        self.blocks = set()
        self._edges = []
        self._arrows = []
        self._edge_paths = []

    @property
    def graph(self):
        return self._graph

    def set_graph(self, v):
        if v is not self._graph:
            self._graph = v
            self.reload()

    def reload(self):
        self.request_relayout()

    def request_relayout(self):
        self._reset_scene()
        if self.graph is None:
            return

        # remove all edges
        scene = self.scene()
        for p in self._edge_paths:
            scene.removeItem(p)

        # remove all nodes
        self.blocks.clear()
        # self.remove_all_children()
        self._edge_paths = []

        # remove existing arrows
        # for arrow in self._arrows:
        # scene.removeItem(arrow)
        self._arrows.clear()

        node_sizes = {}
        for node in self.graph.nodes():
            self.blocks.add(node)
            node_sizes[node] = (node.width, node.height)
        gl = CartGraphLayouter(self.graph, node_sizes, node_compare_key=lambda n: 0)

        self._edges = gl.edges

        min_x, max_x, min_y, max_y = 0, 0, 0, 0

        scene = self.scene()
        for node, (x, y) in gl.node_coordinates.items():
            scene.addItem(node)
            node.setPos(x, y)
            min_x = min(min_x, node.x())
            max_x = max(max_x, node.x() + node.width)
            min_y = min(min_y, node.y())
            max_y = max(max_y, node.y() + node.height)

        for edge in self._edges:
            arrow = QCartEdge(edge, self.cartprograph_view)
            # popuplate edge dict
            self.workspace.cartprograph.edges[(edge.src.id, edge.dst.id)] = arrow
            self._arrows.append(arrow)
            scene.addItem(arrow)
            arrow.setPos(QPointF(*edge.coordinates[0]))

        min_x -= self.LEFT_PADDING
        max_x += self.LEFT_PADDING
        min_y -= self.TOP_PADDING
        max_y += self.TOP_PADDING
        width = (max_x - min_x) + 2 * self.LEFT_PADDING
        height = (max_y - min_y) + 2 * self.TOP_PADDING

        self._reset_view()

    #
    # Private methods
    #

    def _initial_position(self):
        ibr = self.scene().itemsBoundingRect()
        return ibr.center()
