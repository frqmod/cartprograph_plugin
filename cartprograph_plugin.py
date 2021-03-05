import types

import networkx as nx
from PySide2.QtGui import QColor
from PySide2.QtCore import Qt

from angrmanagement.plugins import BasePlugin

from .cartprograph_view import CartprographView
from .cartprograph_client import CartprographClient


class CartprographPlugin(BasePlugin):
    def __init__(self, workspace):
        super().__init__(workspace)

        self.workspace = workspace
        workspace.cartprograph = types.SimpleNamespace()

        self.cartprograph_view = CartprographView(workspace, "center")
        workspace.default_tabs += [self.cartprograph_view]
        workspace.add_view(
            self.cartprograph_view,
            self.cartprograph_view.caption,
            self.cartprograph_view.category,
        )

        workspace.cartprograph.graph = nx.DiGraph()
        workspace.cartprograph.client = CartprographClient(
            workspace,
            workspace.cartprograph.graph,
            lambda node_id: self.cartprograph_view.update_graph(
                workspace.cartprograph.graph
            ),
        )

        workspace.add_disasm_insn_ctx_menu_entry(
            "Cartprograph &filter", self.handle_filter, add_separator_first=True
        )

    def handle_filter(self, context_menu):
        addr = context_menu.insn_addr
        cfg = self.workspace.instance.cfg
        node = cfg.get_any_node(addr, anyaddr=True)
        self.workspace.cartprograph.apply_filter(
            lambda trace: node.addr in trace["basic_blocks"]
        )

    def handle_click_block(self, qblock, event):
        if event.button() == Qt.LeftButton:
            addr = qblock.addr
            # TODO: highlight Cartprograph node traces which include this basic block

    def color_block(self, addr):
        # TODO: QEMU uses super-basic-blocks, we need to convert super-basic-blocks into their set of smaller (angr) basic blocks
        graph = self.workspace.cartprograph.graph
        for node in graph.nodes():
            for traced_address in graph.nodes[node]["basic_blocks"]:
                if traced_address == addr:
                    return QColor(0xDA, 0xFA, 0xFA)
