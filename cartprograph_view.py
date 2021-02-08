import networkx as nx
from PySide2.QtWidgets import (
    QMainWindow,
    QDockWidget,
    QVBoxLayout,
    QPlainTextEdit,
    QLineEdit,
    QTableWidgetItem, QAbstractItemView,
)
from PySide2.QtCore import Qt
from qtpy import QtWidgets
from PySide2 import QtCore
from angrmanagement.ui.views import BaseView
from .qcartblock import QCartBlock
from .qprogramtree import QProgramTree
from angr.knowledge_plugins import Function
from typing import Optional


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
        self.workspace.cartprograph.annotations = {}
        self.selected_item_id = None
        self.highlighted_item_ids = []

        self.G = None

        self._init_widgets()

    def redraw_graph(self):
        if self._carttree is not None:
            self._carttree.viewport().update()



    def update_graph(self, G):
        self.G = G
        # clear nodes/edges dicts
        self.workspace.cartprograph.nodes = {}
        self.workspace.cartprograph.edges = {}
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
        self.workspace.cartprograph.nodes.update({id: QCartBlock(False, self, label=self.node_show(id), id=id, type=self.get_node_type(id), annotation=self.get_annotation(id))})

    def store_annotation(self, id, annotation):
        self.workspace.cartprograph.annotations.update({id: annotation})

    def get_annotation(self, id):
        if id in self.workspace.cartprograph.annotations:
            return self.workspace.cartprograph.annotations[id]
        return ""

    def get_node_type(self, id):
        ints = self.workspace.cartprograph.graph.nodes[id]["interactions"]
        if not ints:
            return None
        if ints[0]["direction"] == "input":
            if ints[0]['data'] is not None:
                return "input"
            else:
                return "pending_input"
        return None # should in theory never happen

    def add_edge(self, id_from, id_to):
        if (id_from, id_to) in self.workspace.cartprograph.edges:
            return
        self.workspace.cartprograph.edges.update({(id_from, id_to): "TEMPORARY"})

    def select_item(self, id):
        #select next node
        self.workspace.cartprograph.nodes[id].selected = True
        if isinstance(self.selected_item_id, int) and not self.selected_item_id == id:
            self.workspace.cartprograph.nodes[self.selected_item_id].selected = False
        #remember what we selcted
        self.selected_item_id = id
        for n in self.highlighted_item_ids:
            if isinstance(n, tuple):
                self.workspace.cartprograph.edges[n].highlighted = False
            else:
                self.workspace.cartprograph.nodes[n].highlighted = False
        #highlight path
        path = nx.shortest_path(self.workspace.cartprograph.graph, source=0, target=id)
        for n in path:
            self.workspace.cartprograph.nodes[n].highlighted = True
            self.highlighted_item_ids.append(n)

        for eout, ein in zip(path, path[1:]):
            self.workspace.cartprograph.edges[(eout, ein)].highlighted = True
            self.highlighted_item_ids.append((eout, ein))



    def node_show(self, id):
        if not self.workspace.cartprograph.graph.nodes[id]["interactions"]:
            return ""
        return "".join(
            e["data"]
            for e in self.workspace.cartprograph.graph.nodes[id]["interactions"]
            if e["data"] is not None
        )

    def update_console(self, id):
        if isinstance(id, tuple):
            id = id[0]
        self.console_output.clear()
        for n in nx.shortest_path(self.workspace.cartprograph.graph, source=0, target=id):
            # TODO: we need to escape any HTML present in data
            node = self.workspace.cartprograph.graph.nodes[n]
            color = "blue" if node["interactions"] and node["interactions"][0]["direction"] == "input" else "black"
            html = f'<div style="color: {color}">' + self.node_show(n).replace("\n", "<br>") + '</div>'
            self.console_output.appendHtml(html)

    def update_tables(self, id):
        self.functable.setRowCount(0)  # clear table
        self.blocktable.setRowCount(0)
        functable_data = [[], [], []]
        blocktable_data = [[],[]]
        for n in nx.shortest_path(self.workspace.cartprograph.graph, source=0, target=id):
            for syscall in self.workspace.cartprograph.graph.nodes[n]["syscalls"]:
                functable_data[0].append(syscall["name"])
                functable_data[1].append(hex(syscall["ret"]) if syscall["ret"] is not None else '')
                functable_data[2].append(", ".join(str(arg) for arg in syscall["args"]))
            for block in self.workspace.cartprograph.graph.nodes[n]["basic_blocks"]:
                blocktable_data[0].append(hex(block))
                blocktable_data[1].append(self._display_block_function(block))

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

    #
    #   Utils
    #

    def _display_block_function(self, block_addr: int) -> str:
        """
        Displays the function associated to the block. Returns empty
        if either the funciton does not exist or the CFG has not been set.

        """
        cfg = self.workspace.instance.cfg
        block = cfg.get_any_node(block_addr)
        if block and block.name:
            return block.name
        functions = self.workspace.instance.kb.functions
        func = functions.get(block_addr)
        if func and func.name:
            return func.name
        return ""

    def _handle_table_click(self, row, col):
        """
        Jumps to disassembly view from a corresponding table location.
        Will go to linear view if the address is outside the range of the graph.
        """
        block_addr = int(self.blocktable.item(row, 0).text(), 16)
        self.workspace.jump_to(block_addr)
    #
    #   Initialize GUI
    #

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
        self.functable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table_tabs.addTab(table_functab, "Syscalls")
        table_functab.layout().addWidget(self.functable)

        self.blocktable = QtWidgets.QTableWidget()
        self.blocktable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table_tabs.addTab(table_blocktab, "Basic Block Trace")
        table_blocktab.layout().addWidget(self.blocktable)
        self.blocktable.cellDoubleClicked.connect(self._handle_table_click)

        table_dock = QDockWidget("Cartprograph Tables", table_tabs)
        main.addDockWidget(Qt.LeftDockWidgetArea, table_dock)
        table_dock.setWidget(table_tabs)

        self.console_output = QPlainTextEdit()
        self.console_output.setReadOnly(True)
        console_group.layout().addWidget(self.console_output)

        self.console_input = QLineEdit()
        console_group.layout().addWidget(self.console_input)
        self.console_input.returnPressed.connect(
            lambda: self.workspace.cartprograph.client.send_input(
                self.selected_item_id, self.console_input.text() + "\n"
            )
        )

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