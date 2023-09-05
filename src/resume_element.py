from typing import Any
from src.constants import SECTION_ATTRIBUTE_MAPPING
from src.utils import dotdict


class ResumeElement:
    def __init__(self, data: dict | dotdict, section_slug: str):
        # logger.debug("Creating resume element with data: %s.", data)
        if not isinstance(data, dict):
            msg = f"A ResumeElement object must be built from a dict, not {type(data)}."
            raise TypeError(msg)

        super().__setattr__("section", section_slug)
        super().__setattr__("_data", data)
        try:
            super().__setattr__("_attribute_mapping", SECTION_ATTRIBUTE_MAPPING[section_slug])
        except KeyError:
            super().__setattr__("_attribute_mapping", {})

    def __getattr__(self, __name: str) -> Any:
        try:
            return self._data[__name]
        except KeyError:
            pass

        try:
            return super().__getattribute__(self._attribute_mapping[__name])
        except (AttributeError, KeyError):
            return None

    def __setattr__(self, __name: str, __value: Any) -> None:
        self._data[__name] = __value

    @property
    def full_summary(self):
        result = self.summary
        if self.highlights:  # If self.highlights is not None and not empty.
            result += "\n<ul>"
            for highlight in self.highlights:
                result += f"\n\t<li>{highlight}</li>"
            result += "\n</ul>"
        return result
