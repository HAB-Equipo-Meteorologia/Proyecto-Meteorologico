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

        self._base_path = Path('frontend/resources/mappings')
        self._color_mappings = None
        self._label_mappings = None
        self._initialized = True

        self._load_resources()

    def _load_resources(self) -> None:
        try:
            with open(self._base_path / 'color_mappings.json', 'r') as f:
                self._color_mappings = json.load(f)

            with open(self._base_path / 'label_mappings.json', 'r') as f:
                self._label_mappings = json.load(f)

            with open(self._base_path / 'element_mappings.json', 'r') as f:
                self._element_mappings = json.load(f)

        except Exception as e:
            print(f"Error loading mappings: {e}")
            raise

    def reload_resources(self) -> None:
        self._load_resources()

    @property
    def choropleth_color_maps(self) -> Dict[str, Any]:
        return self._color_mappings.get('choropleth', {})

    @property
    def histogram_color_maps(self) -> Dict[str, Any]:
        return self._color_mappings.get('histogram', {})

    @property
    def scatter_color_maps(self) -> Dict[str, Any]:
        return self._color_mappings.get('scatter', {})

    @property
    def column_labels(self) -> Dict[str, str]:
        return self._label_mappings.get('columns', {})

    @property
    def numeric_columns(self) -> Dict[str, list]:
        return self._element_mappings.get('numeric', {})
