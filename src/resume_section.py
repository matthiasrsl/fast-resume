from typing import TYPE_CHECKING

from src.constants import SECTION_NAME_L10N
from src.resume_element import ResumeElement

if TYPE_CHECKING:
    from src.resume import Resume


class ResumeSection:
    def __init__(self, key, elements: list[dict], resume: "Resume") -> None:
        if not isinstance(elements, list):
            msg = f"A ResumeSection objects must be build from a list, not {type(elements)}."
            raise TypeError(msg)
        self.slug = key
        self.section_name_l10n = SECTION_NAME_L10N[resume.lang]
        try:
            self.name = self.section_name_l10n[key]
        except KeyError:
            self.name = key.replace("_", " ")
        self.elements = [ResumeElement(element, self.slug, resume) for element in elements]

    def __getitem__(self, index):
        return self.elements[index]

    def __len__(self) -> int:
        return len(self.elements)

    def __iter__(self):
        return iter(self.elements)

    def __repr__(self):
        return f"ResumeSection('{self.name}')"
