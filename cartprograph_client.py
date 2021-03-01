import os
import time

import networkx as nx
import requests
import socketio

from angrmanagement.logic.threads import gui_thread_schedule_async


URL = "http://localhost:4242/"


class GraphUpdateNamespace(socketio.ClientNamespace):
    def __init__(self, workspace, graph, callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workspace = workspace
        self.graph = graph
        self.callback = callback

    def on_update(self, data):
        parent_id, node_id = data["src_id"], data["dst_id"]

        def get_trace(attr):
            return requests.get(f"{URL}/trace/{attr}/{node_id}").json()

        node_attrs = {
            attr: get_trace(attr)
            for attr in ["basic_blocks", "syscalls", "interactions"]
        }

        while True:
            # TODO: clean this up, this is insane
            cfg = self.workspace.instance.cfg
            if cfg is None:
                time.sleep(1)
            else:
                break

        offset = 0x400000 - 0x4000000000
        node_attrs["basic_blocks"] = [
            address + offset
            for address in node_attrs["basic_blocks"]
            if cfg.get_node(address + offset)
        ]

        self.graph.add_node(node_id, **node_attrs)
        if node_id:
            self.graph.add_edge(parent_id, node_id)
        gui_thread_schedule_async(self.callback, args=(node_id,))


class CartprographClient:
    def __init__(self, workspace, graph, update_callback):
        self.workspace = workspace
        self.graph = graph
        self.update_callback = update_callback

        self.client = socketio.Client()
        graph_update_namespace = GraphUpdateNamespace(
            self.workspace, self.graph, self.update_callback
        )
        self.client.register_namespace(graph_update_namespace)
        self.client.connect(URL)

    def send_input(self, node_id, data):
        response = requests.post(f"{URL}/input/{node_id}", json={"input": data})
        assert response.json()["success"]
