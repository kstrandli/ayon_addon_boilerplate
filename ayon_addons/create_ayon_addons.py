import os
import sys
import re
import json
import shutil
import argparse
import zipfile
import platform
import collections
from pathlib import Path
from typing import Any, Optional, Iterable, Pattern, List, Tuple

# Patterns of directories to be skipped for server part of addon
IGNORE_DIR_PATTERNS: List[Pattern] = [
    re.compile(pattern)
    for pattern in {
        # Skip directories starting with '.'
        r"^\.",
        # Skip any pycache folders
        "^__pycache__$"
    }
]

# Patterns of files to be skipped for server part of addon
IGNORE_FILE_PATTERNS: List[Pattern] = [
    re.compile(pattern)
    for pattern in {
        # Skip files starting with '.'
        # NOTE this could be an issue in some cases
        r"^\.",
        # Skip '.pyc' files
        r"\.pyc$"
    }
]


class ZipFileLongPaths(zipfile.ZipFile):
    """Allows longer paths in zip files.

    Regular DOS paths are limited to MAX_PATH (260) characters, including
    the string's terminating NUL character.
    That limit can be exceeded by using an extended-length path that
    starts with the '\\?\' prefix.
    """
    _is_windows = platform.system().lower() == "windows"

    def _extract_member(self, member, tpath, pwd):
        if self._is_windows:
            tpath = os.path.abspath(tpath)
            if tpath.startswith("\\\\"):
                tpath = "\\\\?\\UNC\\" + tpath[2:]
            else:
                tpath = "\\\\?\\" + tpath

        return super(ZipFileLongPaths, self)._extract_member(
            member, tpath, pwd
        )


def _value_match_regexes(value: str, regexes: Iterable[Pattern]) -> bool:
    return any(
        regex.search(value)
        for regex in regexes
    )


def find_files_in_subdir(
    src_path: str,
    ignore_file_patterns: Optional[List[Pattern]] = None,
    ignore_dir_patterns: Optional[List[Pattern]] = None,
    ignore_subdirs: Optional[Iterable[Tuple[str]]] = None
):
    """Find all files to copy in subdirectories of given path.

    All files that match any of the patterns in 'ignore_file_patterns' will
        be skipped and any directories that match any of the patterns in
        'ignore_dir_patterns' will be skipped with all subfiles.

    Args:
        src_path (str): Path to directory to search in.
        ignore_file_patterns (Optional[List[Pattern]]): List of regexes
            to match files to ignore.
        ignore_dir_patterns (Optional[List[Pattern]]): List of regexes
            to match directories to ignore.
        ignore_subdirs (Optional[Iterable[Tuple[str]]]): List of
            subdirectories to ignore.

    Returns:
        List[Tuple[str, str]]: List of tuples with path to file and parent
            directories relative to 'src_path'.
    """

    if ignore_file_patterns is None:
        ignore_file_patterns = IGNORE_FILE_PATTERNS

    if ignore_dir_patterns is None:
        ignore_dir_patterns = IGNORE_DIR_PATTERNS
    output: list[tuple[str, str]] = []

    hierarchy_queue = collections.deque()
    hierarchy_queue.append((src_path, []))
    while hierarchy_queue:
        item: tuple[str, str] = hierarchy_queue.popleft()
        dirpath, parents = item
        if ignore_subdirs and parents in ignore_subdirs:
            continue
        for name in os.listdir(dirpath):
            path = os.path.join(dirpath, name)
            if os.path.isfile(path):
                if not _value_match_regexes(name, ignore_file_patterns):
                    items = list(parents)
                    items.append(name)
                    output.append((path, os.path.sep.join(items)))
                continue

            if not _value_match_regexes(name, ignore_dir_patterns):
                items = list(parents)
                items.append(name)
                hierarchy_queue.append((path, items))

    return output


def read_addon_version(version_path: Path) -> str:
    # Read version
    version_content: dict[str, Any] = {}
    with open(str(version_path), "r") as stream:
        exec(stream.read(), version_content)
    return version_content["__version__"]


def get_addon_version(addon_dir: Path) -> str:
    return read_addon_version(addon_dir / "server" / "version.py")

def create_addon_zip(
    output_dir: Path,
    addon_name: str,
    addon_version: str,
    keep_source: bool
):
    zip_filepath = output_dir / f"{addon_name}-{addon_version}.zip"
    addon_output_dir = output_dir / addon_name / addon_version
    with ZipFileLongPaths(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr(
            "manifest.json",
            json.dumps({
                "addon_name": addon_name,
                "addon_version": addon_version
            })
        )
        # Add client code content to zip
        src_root = os.path.normpath(str(addon_output_dir.absolute()))
        src_root_offset = len(src_root) + 1
        for root, _, filenames in os.walk(str(addon_output_dir)):
            rel_root = ""
            if root != src_root:
                rel_root = root[src_root_offset:]

            for filename in filenames:
                src_path = os.path.join(root, filename)
                if rel_root:
                    dst_path = os.path.join("addon", rel_root, filename)
                else:
                    dst_path = os.path.join("addon", filename)
                zipf.write(src_path, dst_path)

    if not keep_source:
        shutil.rmtree(str(output_dir / addon_name))

    return zip_filepath


def create_addon_package(
    addon_name: str,
    source_client_dir: Path,
    source_server_dir: Path,
    source_service_dir: Path,
    source_pyproject_path: Path,
    output_dir: Path,
    create_zip: bool,
    keep_source: bool,
    exclude_client_subfolders: list = []
):
    '''
    :param addon_name: Name of addon. (Todo: Confirm if it have to match the client package name.)
    :param source_client_dir: Path to package containing addon client code.
    :param source_server_dir: Path to package containing addon server code.
    :param source_pyproject_path: Path to pyproject.toml addon dependency file.
    :param output_dir: Path to directory to assemble and build addons and export zips to.
    :param create_zip:
    :param keep_source:
    :param exclude_client_subfolders: List of lists. Each list containing strings representing nested folders/files that should not be included in the zip.
                            Example: [["vendor", "package-name"]]
    :return:
    '''
    source_version_path = source_client_dir / "version.py"
    addon_version = read_addon_version(source_version_path)

    ### Create temporary addon build folder.
    addon_output_dir = output_dir / addon_name / addon_version
    private_dir = addon_output_dir / "private"
    # Delete temporary build folder if it exists.
    if addon_output_dir.exists():
        shutil.rmtree(str(addon_output_dir))

    # Make sure dir exists
    addon_output_dir.mkdir(parents=True, exist_ok=True)
    private_dir.mkdir(parents=True, exist_ok=True)


    ### Copy Sources to build folder
    # Copy version file.
    shutil.copy(str(source_version_path), str(addon_output_dir))
    # Copy server directory.
    if source_server_dir:
        for subitem in source_server_dir.iterdir():
            if subitem.is_dir():
                shutil.copytree(str(subitem), addon_output_dir / subitem.name)
            else:
                shutil.copy(str(subitem), str(addon_output_dir / subitem.name))
    # Copy server directory.
    if source_service_dir:
        for subitem in source_service_dir.iterdir():
            shutil.copy(str(subitem), str(addon_output_dir / subitem.name))
    # Copy pyproject.toml
    if source_pyproject_path:
        shutil.copy(str(source_pyproject_path), (private_dir / source_pyproject_path.name))

    ### Create zip of source client files.
    if source_client_dir:
        zip_filepath = private_dir / "client.zip"
        with ZipFileLongPaths(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
            for path, sub_path in find_files_in_subdir(str(source_client_dir), ignore_subdirs=exclude_client_subfolders):
                zipf.write(path, f"{source_client_dir.name}/{sub_path}")

    if create_zip:
        filepath = create_addon_zip(output_dir, addon_name, addon_version, keep_source)
        return filepath


def main(
    addon_name,
    source_client_dir=None,
    source_server_dir=None,
    source_service_dir=None,
    source_pyproject_path=None,
    output_dir=None,
    skip_zip=False,
    keep_source=False,
    exclude_client_subfolders=None,
):
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

    if source_client_dir and os.path.exists(source_client_dir):
        source_client_dir = Path(source_client_dir)

    if source_server_dir and os.path.exists(source_server_dir):
        source_server_dir = Path(source_server_dir)

    if source_service_dir and os.path.exists(source_service_dir):
        source_service_dir = Path(source_service_dir)

    if source_pyproject_path and os.path.exists(source_pyproject_path):
        source_pyproject_path = Path(source_pyproject_path)

    if output_dir and os.path.exists(output_dir):
        output_dir = Path(output_dir)
    else:
        output_dir = current_dir / "packages"
    if not os.path.exists(output_dir):
        output_dir.mkdir(parents=True, exist_ok=True)

    create_zip = not skip_zip

    filepath = create_addon_package(
        addon_name=addon_name,
        source_client_dir=source_client_dir,
        source_server_dir=source_server_dir,
        source_service_dir=source_service_dir,
        source_pyproject_path=source_pyproject_path,
        output_dir=output_dir,
        create_zip=create_zip,
        keep_source=keep_source,
        # exclude_client_subfolders=exclude_client_subfolders,
    )

    print(f"Addon Package finished: '{addon_name}' - {filepath}")
    return filepath


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--name",
        dest="addon_name",
        help=(
            "Name of addon"
        )
    )

    parser.add_argument(
        "--source-client-dir",
        dest="source_client",
        default=None,
        help=(
            "Path to package with addon client code."
        )
    )

    parser.add_argument(
        "--source-server-dir",
        dest="source_server",
        default=None,
        help=(
            "Path to package with addon server code"
        )
    )

    parser.add_argument(
        "--source-service-dir",
        dest="source_service",
        default=None,
        help=(
            "Path to addon service code"
        )
    )

    parser.add_argument(
        "--source-pyproject",
        dest="source_pyproject",
        default=None,
        help=(
            "Path to addon pyproject dependency file."
        )
    )


    parser.add_argument(
        "--skip-zip",
        dest="skip_zip",
        action="store_true",
        help=(
            "Skip zipping server package and create only"
            " server folder structure."
        )
    )
    parser.add_argument(
        "--keep-sources",
        dest="keep_sources",
        action="store_true",
        help=(
            "Keep folder structure when server package is created."
        )
    )
    parser.add_argument(
        "-o", "--output",
        dest="output_dir",
        default=None,
        help=(
            "Directory path where package will be created"
            " (Will be purged if already exists!)"
        )
    )
    parser.add_argument(
        "-c", "--clear-output-dir",
        dest="clear_output_dir",
        action="store_true",
        help=(
            "Clear output directory before package creation."
        )
    )
    parser.add_argument(
        "-x", "--exclude-client-subfolders",
        dest="exclude_subfolders",
        action="append",
        default=None,
        help="Exclude given subfolders from client source folder",
    )

    args = parser.parse_args(sys.argv[1:])
    main(
        addon_name=args.addon_name,
        source_client_dir=args.source_client,
        source_server_dir=args.source_server,
        source_service_dir=args.source_service,
        source_pyproject_path=args.source_pyproject,
        output_dir=args.output_dir,
        skip_zip=args.skip_zip,
        keep_source=args.keep_sources,
        exclude_client_subfolders=args.exclude_subfolders,
    )