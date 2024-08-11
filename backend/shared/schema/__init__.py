import glob
import os

import yaml
from cerberus import rules_set_registry, schema_registry

from .validator import Validator

registry = schema_registry


def _load_schema():
    base_path = os.path.dirname(os.path.abspath(__file__))
    files = glob.glob(f"{base_path}/**/*.yml")

    for file_path in files:
        file_full_name, _ = os.path.splitext(file_path)
        file_name = file_full_name.replace(base_path, "")
        namespace = file_name.replace("/", ".")[1:]

        with open(file_path, "r") as stream:
            file_content = yaml.load(stream, Loader=yaml.SafeLoader)

        if "rules." in namespace or namespace.endswith(".rule"):
            rules_set_registry.add(namespace, file_content)
        else:
            schema_registry.add(namespace, file_content)


_load_schema()
