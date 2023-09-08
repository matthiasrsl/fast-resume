import logging
from typing import Any
from src.constants import SECTION_ATTRIBUTE_MAPPING
from src.utils import dotdict

logger = logging.getLogger("LightCvMaker")
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
            try:
                return self._data[self._attribute_mapping[__name]]
            except (KeyError):
                return None


    def __setattr__(self, __name: str, __value: Any) -> None:
        self._data[__name] = __value

    @property
    def full_summary(self):
        result = self.summary or ""
        if self.highlights:  # If self.highlights is not None and not empty.
            result += "\n<ul>"
            for highlight in self.highlights:
                result += f"\n\t<li>{highlight}</li>"
            result += "\n</ul>"
        return result

    @property
    def dates(self) -> str:
        if self.startDate and self.endDate:
            return f"{self.startDate.strf} - {self.endDate}"
        if self.startDate:
            return f"Since {self.startDate}"
        return f"Until {self.endDate}"
