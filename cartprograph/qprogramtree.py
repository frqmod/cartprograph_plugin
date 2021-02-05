import logging

from PySide2.QtCore import Qt, QPointF, QRectF

from .cartgraphlayouter import CartGraphLayouter
from .qcartedge import QCartEdge
from ...ui.widgets.qgraph import QZoomableDraggableGraphicsView


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


        scene = self.scene()
        for node, (x, y) in gl.node_coordinates.items():
            scene.addItem(node)
            node.setPos(x, y)

        for edge in self._edges:
            arrow = QCartEdge(edge, self.cartprograph_view)
            # popuplate edge dict
            self.workspace.cartprograph.edges[(edge.src.id, edge.dst.id)] = arrow
            self._arrows.append(arrow)
            scene.addItem(arrow)
            arrow.setPos(QPointF(*edge.coordinates[0]))

        self._update_scene_boundary()
        self._reset_view()

    #
    # Private methods
    #
    def _update_scene_boundary(self):
        scene = self.scene()
        # Leave some margins
        rect = scene.itemsBoundingRect()  # type: QRectF
        scene.setSceneRect(QRectF(rect.x() - 200, rect.y() - 200, rect.width() + 400, rect.height() + 400))

    def _initial_position(self):
        ibr = self.scene().itemsBoundingRect()
        return ibr.center()
