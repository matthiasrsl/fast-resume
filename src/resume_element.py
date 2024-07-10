import logging
from typing import TYPE_CHECKING, Any

import markdown

if TYPE_CHECKING:
    from src.resume import Resume

from src.constants import L10N, SECTION_ATTRIBUTE_MAPPING
from src.utils import dotdict

logger = logging.getLogger("LightCvMaker")


class ResumeElement:
    def __init__(self, data: dict | dotdict, section_slug: str, resume: "Resume"):
        if not isinstance(data, dict):
            msg = f"A ResumeElement object must be built from a dict, not {type(data)}."
            raise TypeError(msg)

        super().__setattr__("section", section_slug)
        super().__setattr__("_data", data)
        try:
            super().__setattr__("_attribute_mapping", SECTION_ATTRIBUTE_MAPPING[section_slug])
        except KeyError:
            super().__setattr__("_attribute_mapping", {})

        self.resume = resume

    def __getattr__(self, __name: str) -> Any:
        try:
            return self._data[__name]
        except KeyError:
            try:
                return self._data[self._attribute_mapping[__name]]
            except KeyError:
                return None

    def __setattr__(self, __name: str, __value: Any) -> None:
        self._data[__name] = __value

    @property
    def full_summary(self):
        result = self.summary or ""
        if self.highlights:  # If self.highlights is not None and not empty.
            for highlight in self.highlights:
                result += f"  \n- {highlight}"
        return markdown.markdown(result)

    @property
    def dates(self) -> str:
        if self.startDate and self.endDate:
            return (
                f"{self.startDate.strftime(self.resume.date_format)}"
                f" - {self.endDate.strftime(self.resume.date_format)}"
            )
        if self.startDate:
            return f"{L10N[self.resume.lang]['date_since']} {self.startDate.strftime(self.resume.date_format)}"
        return f"{L10N[self.resume.lang]['date_since']} {self.endDate.strftime(self.resume.date_format)}"
