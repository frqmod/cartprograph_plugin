from types import SimpleNamespace
import networkx as nx
import itertools
import string
import random
from angrmanagement.plugins import BasePlugin
from PySide2.QtWidgets import QMessageBox
from angrmanagement.plugins.cartprograph.cartprograph_view import CartprographView


class Cartprograph(BasePlugin):
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

        workspace.cartprograph.graph = self.init_graph()
        self.cartprograph_view.update_graph(workspace.cartprograph.graph)

    def init_graph(self):
        graph = CartprographGenerator()
        return graph.graph

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


class CartprographGenerator:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.new_id = itertools.count()

        self.generate_graph()

    def generate_graph(self):
        for i in range(random.randrange(10, 20)):
            self.new_node()
            # print(f"NODE {i}")
            # print(self.node_show(i))
            # print("=" * 80)

    def random_basic_blocks(self):
        return [
            0x400000 + random.randrange(0, 100) for _ in range(random.randrange(10, 20))
        ]

    def random_syscalls(self):
        num_elements = random.randrange(2, 7)
        indexes = sorted(random.sample(list(range(10)), k=num_elements))
        return [
            {
                "nr": random.randrange(0, 50),
                "args": [
                    random.randrange(0, 0x1000) for _ in range(random.randrange(0, 4))
                ],
                "ret": random.randrange(0, 100),
                "basic_block_index": indexes[i],
            }
            for i in range(num_elements)
        ]

    def random_interactions(self):
        direction = random.choice(["input", "output"])
        num_elements = random.randrange(2, 7)
        indexes = sorted(random.sample(list(range(10)), k=num_elements))
        return [
            {
                "channel": "stdio",
                "direction": direction,
                "data": "".join(
                    random.choices(
                        string.ascii_letters + " " * 5 + "\n",
                        k=random.randrange(10, 20),
                    )
                ).strip()
                + "\n",
                "basic_block_index": indexes[i],
            }
            for i in range(num_elements)
        ]

    def new_node(self):
        node_id = next(self.new_id)
        parent_id = random.randrange(0, node_id) if node_id else None
        self.graph.add_node(
            node_id,
            parent_id=parent_id,
            basic_blocks=self.random_basic_blocks(),
            syscalls=self.random_syscalls(),
            interactions=self.random_interactions(),
        )
        if parent_id is not None:
            self.graph.add_edge(
                parent_id,
                node_id,
                basic_blocks=self.random_basic_blocks(),
                syscalls=self.random_syscalls(),
            )

