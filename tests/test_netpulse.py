import json
from pathlib import Path


def test_config():
    config_path = Path(__file__).parents[1] / "config.json"
    config = json.loads(config_path.read_text())
    assert config["network"].endswith("/24")
