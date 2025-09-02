import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from zfn_api import Client


def test_client_can_instantiate():
    client = Client()
    assert isinstance(client, Client)
