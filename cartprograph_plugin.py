import types

import networkx as nx

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
        insn_addr = context_menu.insn_addr
        self.workspace.cartprograph.apply_filter(
            lambda trace: insn_addr in trace["basic_blocks"]
        )
