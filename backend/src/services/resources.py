import json
from pathlib import Path
from typing import Dict, Any


class ResourceManager:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._base_path = Path('backend/data')
        self._color_mappings = None
        self._label_mappings = None
        self._initialized = True

        self._load_resources()

    def _load_resources(self) -> None:
        try:
            with open(self._base_path / 'mappings/element_mappings.json', 'r') as f:
                self._element_mappings = json.load(f)
        except Exception as e:
            print(f"Error loading mappings: {e}")
            raise

    def reload_resources(self) -> None:
        self._load_resources()

    @property
    def elements_map(self) -> Dict[str, Any]:
        return self._element_mappings.get('elements', {})

    @property
    def element_columns(self) -> Dict[str, Any]:
        return self._element_mappings.get('columns', {})
