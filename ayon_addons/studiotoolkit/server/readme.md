Here we define the addon for the Ayon Server.

### server/settings/main.py
Here we define the settings available on the server for the addon.
- Rename the BaseSettingsModel class.
"MyAddonSettings"
"SceneManagerSettings"
"StudioToolkitSettings"

### server/settings/__init__.py
Make the BaseSettingsModel class "MyAddonSettings" available to be imported from the package "settings", instead of the module "main".
Update the import statement and class name in the __all__ tuple to match whatever name you gave the BaseSettingsModel class in main.py.

### server/__init__.py:
Here we define addon for Ayon Server

- Rename the BaseServerAddon class.
"MyAddonAddon"
"SceneManagerAddon"
"StudioToolkitAddon"


- Link the BaseServerAddon to the BaseSettingsModel
Rename the imported classes to match the BaseSettingsModel defined in the server/settings/main.py
Link it to the settings model in the BaseServerAddon class.
