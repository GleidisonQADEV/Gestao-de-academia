import json
import os

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "version.json")


def get_version() -> str:
    try:
        with open(_CONFIG_PATH, "r") as f:
            return json.load(f).get("version", "V1")
    except Exception:
        return "V1"


def set_version(version: str):
    try:
        with open(_CONFIG_PATH, "w") as f:
            json.dump({"version": version}, f)
    except Exception as e:
        print(f"Erro ao salvar versão: {e}")
