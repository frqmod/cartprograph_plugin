from types import SimpleNamespace
import networkx as nx
import itertools
import string
import random
from angrmanagement.plugins import BasePlugin
from PySide2.QtWidgets import QMessageBox
from .cartprograph_view import CartprographView
from .cartprograph_client import initialize_client


class CartprographPlugin(BasePlugin):
    # adds menu options to the Plugin dropdown
    MENU_BUTTONS = ["Open Messagebox"]

    def __init__(self, workspace):
        super().__init__(workspace)
        workspace.cartprograph = SimpleNamespace()
        self.cartprograph_view = CartprographView(workspace, "center")
        workspace.default_tabs += [self.cartprograph_view]
        workspace.add_view(
            self.cartprograph_view,
            self.cartprograph_view.caption,
            self.cartprograph_view.category,
        )

        workspace.cartprograph.graph = nx.DiGraph()

        initialize_client(
            workspace.cartprograph.graph,
            lambda node_id: self.cartprograph_view.update_graph(
                workspace.cartprograph.graph
            ),
        )

    # handles the MENU_OPTIONS
    def handle_click_menu(self, idx):
        if idx < 0 or idx >= len(self.MENU_BUTTONS):
            return

        # not sure why this is here
        if self.workspace.instance.project is None:
            print("WARN: Project is None.")

        if idx == 0:  # bad, fix later.
            QMessageBox.critical(
                self.workspace._main_window, "Test!", "This is a test. You caused this."
            )
