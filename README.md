# ayon_addon_boilerplate
Example structure for custom Ayon addon for integrating custom tools and pipelines into the Ayon Framework.

# Before you start
This example may quickly become out of date as Ayon receives updates, and the best practices changes.
My example is a result of experimation and making stuff work for my particular needs, which may not correlate with the intended ways of approaching this problem from Ayon's perspective.

Ayon developers recommends working within the intended Ayon Addon structure directly.
However, my needs was to develop a method that allowed me integrate studio tools into Ayon, despite the tool not having been developed exclusively as an Ayon addon from the start. Or if the tool should be able to operate independently from Ayon if needed.
Because of this, all ayon-logic has been kept separate where possible, and the addon itself works as a wrapper around a core studio pipeline toolkit.

# How to Use
In this example, the addon name is "studiotoolkit", and all studio toolkit code has eben developed in the core package named "core".
The addon name "studiotoolkit" is for Ayon Server logic, where the package name "core" can be named separately.
"core" will be added to PYTHON_PATH, and will be available as a python package for all other Ayon addons.

### Rename example addon name
Rename all relevant classes and name variables to the desired addon name.
All name variables with the example "studiotoolkit" should be renamed to your particular addon name, and must be consistent across all locations:

### Setup Ayon Addon Structure (BaseServerAddon + BaseSettingsModel classes)
Create a folder for the addon in the ayon_addons directory. Create subfolders "client" and "server".
./ayon_addons/studiotoolkit/client/
This is where the client-side code ("./core") should be, but it is included in the build process instead when generating the addon-zip file.

./ayon_addons/studiotoolkit/server/
Here is Server-side setup, which is required to distribute client-side code and make everything work.
See readme in example for more details.

### Setup "Core" package & Ayon Tray Integration (OpenPypeModule class)
The "core" package is the main client-facing python package which is the root of all imports for the tool. This package will be available in PYTHON_PATH for other addons to use.
This directory would normally exist in the "client"-folder in a traditional Ayon Addon structure.

To integrate into the Ayon Tray, Ayon will look for a OpenPypeModule class accessible from "core".
This class has been setup in ./core/ayon_addon.py, and exposed to the core-package by including it in __all__ inside ./core/__init__.py.
To prevent the package from breaking when used outside Ayon where the OpenPypeModule class is unavailable, the __all__ inclusion has been it has been wrapped in a try/except.
(OpenPypeModule is likely to be replaced soon as Ayon API is being updated and refactored to remove legacy OpenPype references)

### Update Package Dependencies with pyproject.toml
Define all package dependencies for the addon, which will be used when generating the Ayon Dependency Package for bundles.
Rename the name-variable to match the addon-name.
Caution - This must be compatible with all other addons on Ayon. You cannot have multiple versions of a single package dependency for separate addons.

### version.py
This is used to define the version of an addon as seen on Ayon Server. Update accordingly.

### Build Ayon Addon
Configure ./ayon_build_addons.py with the correct addon name, and point it to the main python package ("core" in this case).
Run the module, and it will assemble the ayon addon and generate a zip ready to be uploaded to the Ayon Server inside ./ayon_addons/packages

# Dev Mode
To use Dev Mode, you must point the addon's local path in the development bundle to the client directory ./ayon_addons/addonname/client, where it expects to find a single python package ("core" in this case).
Since this boilerplate structure has the core package outside the client directory, dev mode will not work.
To work around this, you may create a relative symlink to ./core inside ./ayon_addons/studiotoolkit/client


# Troubleshooting:
After uploading the packaged zip to Ayon Server, if the addon fails to show up, inspect the event viewer.
If *any* version of an addon package throws an error, the whole addon will fail to load.
If you try to apply a fix in v0.0.4, but v0.0.2 is still on the server with the error, then v0.0.4 will not show up either.
In that case, delete the old addon versions manually from the Ayon Server storage and restart the server.

