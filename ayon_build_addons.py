import os
from pathlib import Path
from ayon_addons import create_ayon_addons

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
addon_output_dir = current_dir / "ayon_addons" / "packages"
source_version_path = source_root / "version.py"

### UPDATE THESE VARIABLES
addon_name = "studiotoolkit"
source_client_dir = current_dir / "core"


if __name__ == '__main__':
    result = create_ayon_addons.main(
        addon_name=addon_name,
        source_client_dir= source_client_dir,
        source_server_dir= current_dir / "ayon_addons" / addon_name / "server",
        source_pyproject_path= source_client_dir / "pyproject.toml",
        output_dir=addon_output_dir,
        skip_zip=False,
        keep_source=False,
        # ignored_client_subpaths=[]
    )
    print('Result:', result)
    print("Done!")

