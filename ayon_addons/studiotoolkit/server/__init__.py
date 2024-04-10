from typing import Any, Type
from ayon_server.addons import StudioToolkitSettings

from .settings import StudioToolkitSettings, DEFAULT_VALUES
from .version import __version__

class StudioToolkitAddon(BaseServerAddon):
    name = "studiotoolkit"
    title = "StudioToolkit"
    version = __version__
    settings_model = MyAddonSettings

    async def get_default_settings(self):
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_VALUES)
