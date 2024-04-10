# ayon_addon_boilerplate
Example structure for custom Ayon addon for integrating custom tools and pipelines into the Ayon Framework.
This example may quickly become out of date as Ayon receives updates, and the best practices changes.
My example is a result of experimation and making stuff work for my particular needs, which may not correlate with the intended ways of approaching this problem from Ayon's perspective.

Ayon developers recommends working within the intended Ayon Addon structure directly.
However, my needs was to develop a method that allowed me integrate studio tools into Ayon, despite the tool not having been developed exclusively as an Ayon addon from the start. Or if the tool should be able to operate independently from Ayon if needed.
Because of this, all ayon-logic has been kept separate where possible, and the addon itself works as a wrapper around a core studio pipeline toolkit.

# Troubleshooting:
After uploading the packaged zip to Ayon Server, if the addon fails to show up, inspect the event viewer.
If *any* version of an addon package throws an error, the whole addon will fail to load.
If you try to apply a fix in v0.0.4, but v0.0.2 is still on the server with the error, then v0.0.4 will not show up either.
In that case, delete the old addon versions manually from the Ayon Server storage and restart the server.
