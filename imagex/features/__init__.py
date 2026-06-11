import importlib
import pkgutil
from pathlib import Path

REGISTRY: dict[str, dict] = {}


def _register(module):
    name = getattr(module, "NAME", None)
    description = getattr(module, "DESCRIPTION", "")
    run_func = getattr(module, "run", None)

    if name and run_func:
        REGISTRY[name] = {
            "name": name,
            "description": description,
            "run": run_func,
            "module": module.__name__,
        }


_features_dir = Path(__file__).parent
for _finder, _name, _ispkg in pkgutil.iter_modules([str(_features_dir)]):
    if _name != "__init__":
        _module = importlib.import_module(f".{_name}", __package__)
        _register(_module)


def get_features() -> dict[str, dict]:
    return dict(REGISTRY)
