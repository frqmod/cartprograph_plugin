from angrmanagement.plugins import BasePlugin
from typing import List
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QMessageBox


class Cartprograph(BasePlugin):
    def __init__(self, workspace):
        super().__init__(workspace)

        workspace.instance.register_container('bookmarks', lambda: [], List[int], 'Bookmarked addresses')

    MENU_BUTTONS = ('Add Bookmark', 'Open Messagebox')

    def handle_click_menu(self, idx):
        if idx < 0 or idx >= len(self.MENU_BUTTONS):
            return
        if self.workspace.instance.project is None:
            print("WARN: Project is None.")

        if idx == 1: #bad, fix later.
            QMessageBox.critical(self.workspace._main_window, "Test!", "This is a test. You caused this.")
        
