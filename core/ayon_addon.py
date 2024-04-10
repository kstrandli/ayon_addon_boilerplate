"""
Discovery classes and modules for Ayon integration.
"""
import os
from qtpy import QtWidgets
from openpype.modules import (OpenPypeModule, ITrayModule, IPluginPaths)

import logging
log = logging.getLogger(__name__)

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

class StudioToolkit(OpenPypeModule, ITrayModule, IPluginPaths):
    name = "studiotoolkit"
    enabled = True
    tray_wrapper = None

    def initialize(self, addon_settings):
        '''
        Initialize the addon.
        For addon settings to work, the class variable "name" must match between this client-addon and BaseServerAddon class in settings.
        Example (Getting addon settings):
            self.addon_settings = addon_settings.get(self.name, dict())
            self._shotgrid_server_url = self.addon_settings.get("shotgrid_server")
        '''
        self.addon_settings = addon_settings.get(self.name)

    def get_plugin_paths(self):
        return {}

    def tray_init(self):
        self.tray_wrapper = TrayMenuWrapper(self)

    def tray_start(self):
        '''Functions to run when booting up the Tray Applications. Such as a GUI asking for Shotgrid login information
        Example:
          return self.tray_wrapper.set_username_label()
        '''
        return self.tray_wrapper

    def tray_exit(self, *args, **kwargs):
        return self.tray_wrapper

    def tray_menu(self, tray_menu):
        return self.tray_wrapper._tray_menu(tray_menu)






class TrayMenuWrapper:
    """Class for adding menu actions to the Ayon tray.

    """
    def __init__(self, addon):
        self.addon = addon
        self.addon_settings = self.addon.addon_settings

        ### To use as parent
        self._tray = None

    def _tray_menu(self, tray_menu):
        """Add menu actions to Ayon tray.

        Args:
            tray_menu (QtWidgets.QMenu): The Ayon Tray menu.
        """
        self._tray = tray_menu


        action = QtWidgets.QAction("Publisher", parent=tray_menu)
        toolkitMenu.addAction(action)
        action.triggered.connect(self.show_publisher)

        toolkitMenu = QtWidgets.QMenu("Studio Toolkit", tray_menu)
        tray_menu.addMenu(toolkitMenu)

        action = QtWidgets.QAction("Fancy Tool A", parent=tray_menu)
        toolkitMenu.addAction(action)
        action.triggered.connect(self.launch_tool_A)

        action = QtWidgets.QAction("Fancy Tool B", parent=tray_menu)
        toolkitMenu.addAction(action)
        action.triggered.connect(self.launch_tool_B)

    def launch_tool_A(self):
        pass

    def launch_tool_B(self):
        pass

    def show_publisher(self):
        from core.tools.publisher import window
        self._publisher_settings = {
            "ftp_user": self.addon_settings.get("studio_ftp_user"),
            "ftp_pw": self.addon_settings.get("studio_ftp_password"),
        }
        self._layoutBuilder_app = window.PublisherWindow(settings=self._publisher_settings)
        self._layoutBuilder_app.show()
        self._layoutBuilder_app.activateWindow()
        self._layoutBuilder_app.raise_()
