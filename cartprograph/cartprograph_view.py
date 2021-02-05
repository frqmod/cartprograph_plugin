import networkx as nx
from PySide2.QtWidgets import (
    QMainWindow,
    QDockWidget,
    QVBoxLayout,
    QPlainTextEdit,
    QLineEdit,
    QTableWidgetItem,
)
from PySide2.QtCore import Qt
from qtpy import QtWidgets
from PySide2 import QtCore
from .qcartblock import QCartBlock
from .qprogramtree import QProgramTree
from ...ui.views import BaseView


class CartprographView(BaseView):
    def __init__(self, workspace, *args, **kwargs):
        super(CartprographView, self).__init__(
            "cartprograph", workspace, *args, **kwargs
        )
        self.caption = "Cartprograph"
        self._carttree = None
        self.workspace = workspace

        self.workspace.cartprograph.nodes = {}
        self.workspace.cartprograph.edges = {}
        self.selected_item_id = None

        self._init_widgets()

    def redraw_graph(self):
        if self._carttree is not None:
            self._carttree.viewport().update()

    def update_graph(self, G):
        # clear nodes/edges dicts
        self.workspace.cartprograph.nodes = self.workspace.cartprograph.edges = {}
        self.workspace.cartprograph.displayGraph = nx.DiGraph()
        for n in G.nodes:
            self.add_node(n)
        for e in G.edges:
            self.add_edge(e[0], e[1])
            self.workspace.cartprograph.displayGraph.add_edge(
                self.workspace.cartprograph.nodes[e[0]],
                self.workspace.cartprograph.nodes[e[1]],
            )
        self._carttree.set_graph(self.workspace.cartprograph.displayGraph)

    def add_node(self, id):
        # check if id exists already
        if id in self.workspace.cartprograph.nodes:
            return
        self.workspace.cartprograph.nodes.update({id: QCartBlock(False, self, label=self.node_show(id), id=id)})

    def add_edge(self, id_from, id_to):
        if (id_from, id_to) in self.workspace.cartprograph.edges:
            return
        self.workspace.cartprograph.edges.update({(id_from, id_to): "TEMPORARY"})

    def select_item(self, id):
        #select next node
        if isinstance(id, tuple):
            self.workspace.cartprograph.edges[id].selected = True
        else:
            self.workspace.cartprograph.nodes[id].selected = True
        #deselect old one
        if isinstance(self.selected_item_id, tuple):
            self.workspace.cartprograph.edges[self.selected_item_id].selected = False
        elif isinstance(self.selected_item_id, int):
            self.workspace.cartprograph.nodes[self.selected_item_id].selected = False
        #remember what we selcted
        self.selected_item_id = id

    def node_show(self, id):
        if not self.workspace.cartprograph.graph.nodes[id]["interactions"]:
            return ""
        return "".join(e["data"] for e in self.workspace.cartprograph.graph.nodes[id]["interactions"])

    def update_console(self, id):
        if isinstance(id, tuple):
            id = id[0]
        self.console_output.clear()
        for n in nx.shortest_path(self.workspace.cartprograph.graph, source=0, target=id):
            self.console_output.appendHtml("<b>" + self.node_show(n) + "</b>")

    def update_tables(self, id):
        self.functable.setRowCount(0)  # clear table
        self.blocktable.setRowCount(0)
        functable_data = [[], [], []]
        blocktable_data = [[],[]]
        for n in nx.shortest_path(self.workspace.cartprograph.graph, source=0, target=id):
            for syscall, block in zip(self.workspace.cartprograph.graph.nodes[n]["syscalls"],self.workspace.cartprograph.graph.nodes[n]["basic_blocks"]):
                functable_data[0].append(hex(syscall["nr"]))
                functable_data[1].append(hex(syscall["ret"]))
                functable_data[2].append(", ".join(str(arg) for arg in syscall["args"]))
                blocktable_data[0].append(hex(block))
                blocktable_data[1].append("todo: find w/ angr") # TODO: resolve func addr w/ angr

        self.functable.setRowCount(len(functable_data[0]))
        self.functable.setColumnCount(len(functable_data))
        self.functable.setHorizontalHeaderLabels(["syscall", "ret val", "args"])
        for row, arr in enumerate(functable_data):
            for col, value in enumerate(arr):
                self.functable.setItem(col, row, QTableWidgetItem(str(value)))
        self.functable.resizeColumnsToContents()

        self.blocktable.setRowCount(len(blocktable_data[0]))
        self.blocktable.setColumnCount(len(blocktable_data))
        self.blocktable.setHorizontalHeaderLabels(["address", "function"])
        for row, arr in enumerate(blocktable_data):
            for col, value in enumerate(arr):
                self.blocktable.setItem(col, row, QTableWidgetItem(str(value)))
        self.blocktable.resizeColumnsToContents()



    def _init_widgets(self):
        main = QMainWindow()
        main.setWindowFlags(Qt.Widget)

        carttree = QProgramTree(
            self.workspace, self
        )
        self._carttree = carttree
        carttree_dock = QDockWidget("Cartprograph Tree", carttree)
        main.setCentralWidget(carttree_dock)
        carttree_dock.setWidget(carttree)

        console_group = QtWidgets.QGroupBox()
        console_group.setLayout(QtWidgets.QVBoxLayout(console_group))
        console_dock = QDockWidget("Cartprograph Console", console_group)
        main.addDockWidget(Qt.BottomDockWidgetArea, console_dock)
        console_dock.setWidget(console_group)

        table_tabs = QtWidgets.QTabWidget()
        table_functab = QtWidgets.QWidget()
        table_functab.setLayout(QtWidgets.QVBoxLayout(table_functab))
        table_blocktab = QtWidgets.QWidget()
        table_blocktab.setLayout(QtWidgets.QVBoxLayout(table_blocktab))

        self.functable = QtWidgets.QTableWidget()
        table_tabs.addTab(table_functab, "Functions")
        table_functab.layout().addWidget(self.functable)

        self.blocktable = QtWidgets.QTableWidget()
        table_tabs.addTab(table_blocktab, "Basic Block Trace")
        table_blocktab.layout().addWidget(self.blocktable)

        table_dock = QDockWidget("Cartprograph Tables", table_tabs)
        main.addDockWidget(Qt.LeftDockWidgetArea, table_dock)
        table_dock.setWidget(table_tabs)

        self.console_output = QPlainTextEdit()
        self.console_output.setReadOnly(True)
        console_group.layout().addWidget(self.console_output)

        self.console_input = QLineEdit()
        console_group.layout().addWidget(self.console_input)

        main_layout = QVBoxLayout()

        main_layout.addWidget(main)
        self.setLayout(main_layout)

#NOTE: this class isn't strictly useful right now, but might be in the future
class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data=None):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if self._data is not None:
            if role == Qt.DisplayRole:
                return self._data[index.column()][index.row()]
        return 0

    def rowCount(self, index):
        if self._data is not None:
            return len(self._data[0])
        else:
            return 0

    def columnCount(self, index):
        if self._data is not None:
            return len(self._data)
        else:
            return 0
