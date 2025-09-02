import importlib.util
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "zfn_api", root / "__init__.py", submodule_search_locations=[str(root)]
)
pkg = importlib.util.module_from_spec(spec)
sys.modules["zfn_api"] = pkg
spec.loader.exec_module(pkg)

from zfn_api import Client


def test_client_can_instantiate():
    client = Client()
    assert isinstance(client, Client)
