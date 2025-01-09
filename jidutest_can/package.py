import pathlib
from importlib.metadata import version
from importlib.metadata import PackageNotFoundError


bin_name = "jidutest-can"
project_name = "jidutest-can"
pkg_name = "jidutest_can"

try:
    __version__ = version(pkg_name)
except PackageNotFoundError:
    __version__ = None

package_path = pathlib.Path(__file__).parent.absolute()
libc_path = package_path / "canlibc"
