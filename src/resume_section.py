from src.resume_element import ResumeElement


class ResumeSection:
    def __init__(self, key, elements: list[dict]) -> None:
        # logger.debug("Creating resume section with elements: %s", elements)
        if not isinstance(elements, list):
            msg = f"A ResumeSection objects must be build from a list, not {type(elements)}."
            raise TypeError(msg)
        self.slug = key
        self.name = key.capitalize()
        self.elements = [ResumeElement(element, self.slug) for element in elements]

    def __getitem__(self, index):
        return self.elements[index]

    def __len__(self) -> int:
        return len(self.elements)

    def __iter__(self):
        return iter(self.elements)

    def __repr__(self):
        return f"ResumeSection('{self.name}')"
