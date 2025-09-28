import pkgutil
from importlib import import_module


def _get_all_extensions() -> list[str]:
    """Recursively discover all Python extensions in the cogs directory."""
    extensions: list[str] = []

    def _discover_extensions(package_name: str) -> None:
        try:
            package = import_module(package_name)
            if not hasattr(package, "__path__"):
                return
            for _, module_name, ispkg in pkgutil.iter_modules(
                package.__path__,
                f"{package_name}.",
            ):
                if ispkg:
                    _discover_extensions(module_name)
                else:
                    extensions.append(module_name)
        except ImportError:
            pass

    _discover_extensions(__package__ or "src.cogs")
    return extensions


EXTENSIONS = _get_all_extensions()
