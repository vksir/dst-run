from enum import Enum
from typing import List, Any


class DataLib:
    @classmethod
    def filter_value_none(cls, data):
        if not isinstance(data, dict):
            return data
        return {key: cls.filter_value_none(value)
                for key, value in data.items() if value is not None}

    @staticmethod
    def filter_key(data: dict, keys: List[Any]):
        return {key: value
                for key, value in data.items() if key not in keys}

    @classmethod
    def deep_update(cls, origin: dict, new_data: dict):
        for key, value in new_data.items():
            if isinstance(value, dict) and key in origin:
                cls.deep_update(origin[key], value)
            else:
                origin[key] = value

    @classmethod
    def convert_value_to_str(cls, data):
        if not isinstance(data, dict):
            return data

        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = cls.convert_value_to_str(value)
            elif isinstance(value, Enum):
                data[key] = value.value
            elif isinstance(value, bool):
                data[key] = 'true' if value else 'false'
            else:
                data[key] = str(value)
        return data
