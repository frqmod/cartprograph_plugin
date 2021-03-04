from functools import partial
from typing import Callable

from ...ui.menus.menu import Menu, MenuEntry, MenuSeparator


class QCartBlockContextMenu(Menu):
    def __init__(self, cartprograph_view):
        super().__init__("", parent=cartprograph_view)
        self.cartprograph_view = cartprograph_view
        self.id = None

        self.entries.extend([
            MenuEntry('&Annotate State', self._annotate_state),
            MenuEntry('&Delete', self._delete_state)
        ])

    def _annotate_state(self):
        self.cartprograph_view.annotate_state(self.id)

    def _delete_state(self):
        print("DELETE")



    #
    # Public Methods
    #

    def add_menu_entry(self, text, callback: Callable[['DisasmLabelContextMenu'], None], add_separator_first=True):
        if add_separator_first:
            self.entries.append(MenuSeparator())
        self.entries.append(MenuEntry(text, partial(callback, self)))

    def remove_menu_entry(self, text, remove_preceding_separator=True):
        for idx, m in enumerate(self.entries):
            if not isinstance(m, MenuEntry):
                continue
            if m.caption == text:
                self.entries.remove(m)
                if remove_preceding_separator:
                    self.entries.pop(idx-1)
