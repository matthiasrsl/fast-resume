import json
import datetime as dt
import logging
import logging.config
from pathlib import Path
import re
import sys
from typing import Any

from jinja2 import Template, Environment, FileSystemLoader
from jinja2.exceptions import TemplateSyntaxError


logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger("LightCvMaker")

env = Environment(loader=FileSystemLoader("templates/"))

services = {
    "linkedin": ("linkedin.com/in/", "https://linkedin.com/in/"),
    "github": ("github.com/", "https://github.com/"),
    "twitter": ("twitter.com/", "https://twitter.com/"),
    "instagram": ("instagram.com/ ", "https://instagram.com/"),
}

DEFAULT_SECTIONS = {
    "work",
    "volunteer",
    "education",
    "awards",
    "certificates",
    "publications",
    "skills",
    "languages",
    "interests",
    "references",
    "projects",
}

SECTION_ATTRIBUTE_MAPPING = {
    "work": {
        "label": "position",
        "organization": "name",
        "startDate": "startDate",
        "endDate": "endDate",
        "location": "location",
        "keywords": "keywords",
        "summary": "summary",
        "highlights": "highlights",
        "description": "full_summary",
        "url": "url",
    },
    "education": {
        "label": "area_and_study_type",
        "organization": "institution",
        "startDate": "startDate",
        "endDate": "endDate",
        "location": "location",
        "summary": "summary",
        "highlights": "courses",
        "description": "full_summary",
        "url": "url",
        "score": "score",
    },
    "volunteer": {
        "label": "position",
        "organization": "organization",
        "startDate": "startDate",
        "endDate": "endDate",
        "location": "location",
        "keywords": "keywords",
        "summary": "summary",
        "highlights": "highlights",
        "description": "full_summary",
        "url": "url",
    },
    "languages": {
        "label": "language",
        "organization": "full_fluency",
        "summary": "certificates_as_str",
        "score": "fluencyNum",
    },
    "projects": {
        "label": "name",
        "organization": "organization",
        "startDate": "startDate",
        "endDate": "endDate",
        "keywords": "keywords",
        "summary": "summary",
        "highlights": "highlights",
        "description": "full_summary",
        "url": "url",
    },
    "open_source": {
        "label": "name",
        "keywords": "keywords",
        "summary": "summary",
        "highlights": "highlights",
        "url": "url",
    },
    "awards": {
        "label": "title",
        "organization": "issuer",
        "startDate": "date",
        "summary": "summary",
    },
    "publications": {
        "label": "name",
        "organization": "publisher",
        "startDate": "releaseDate",
        "location": "location",
        "summary": "summary",
        "url": "url",
    },
    "skills": {
        "label": "name",
        "keywords": "keywords",
        "summary": "summary",
        "score": "level",
    },
    "traits": {
        "label": "name",
        "summary": "summary",
    },
    "certificates": {
        "label": "name",
        "organization": "issuer",
        "startDate": "date",
        "url": "url",
    },
    "interests": {
        "label": "name",
        "keywords": "keywords",
        "summary": "summary",
    },
    "references": {
        "label": "name",
        "organization": "company",
        "summary": "reference",
        "url": "email",
    },
}
class dotdict(dict):  # noqa: N801
    """
    A dictionary supporting dot notation.
    """

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    @staticmethod
    def convert_to_dotdict(obj: object) -> object:
        if isinstance(obj, dict):
            return dotdict(obj)
        if isinstance(obj, list):
            return [dotdict.convert_to_dotdict(elt) for elt in obj]
        return obj

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in self.items():
            self[k] = dotdict.convert_to_dotdict(v)


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
            return getattr(self, self._attribute_mapping[__name])
        except KeyError:
            return None

    def __setattr__(self, __name: str, __value: Any) -> None:
        self._data[__name] = __value

    @property
    def full_summary(self):
        result = f"<p>{self.summary}</p>\n<ul>"
        if self.highlights:  # If self.highlights is not None and not empty.
            for highlight in self.highlights:
                result += f"\n\t<li>{highlight}</li>"
            result += "\n</ul>"
        return result

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


class Resume:
    def __init__(self, name):
        logger.debug("Creating Resume %s.", name)
        with open(f"resumes/{name}.json") as file:
            raw_data = file.read()
            self._data = dotdict(json.loads(raw_data))
            self.name = name
            self._technical_sections_keys = set(self._data)
            self._section_keys = self._technical_sections_keys - {"basics", "meta"}
            self._additional_section_keys = self._section_keys - DEFAULT_SECTIONS
            self._default_section_keys = self._section_keys - self._additional_section_keys

            # try:
            #     birthdate = dt.datetime.strptime(
            #         self._data["person"]["birthdate"], "%Y-%m-%d"
            #     )
            #     self._data["person"]["age"] = str(
            #         int((dt.datetime.now() - birthdate).days / 365.25)
            #     )
            # except ValueError:
            #     self._data["person"]["age"] = "Error"
            # except KeyError:
            #     pass  # Birthdate not displayed.

            # for i, account in enumerate(self._data["person"]["usernames"]):
            #     if account["service"] in services:
            #         self._data["person"]["usernames"][i]["link"] = (
            #             services[account["service"]][1] + account["username"]
            #         )

            # for section in self._data["sections"]:
            #     if section["type"] == "experience":
            #         for element in section["contents"]:
            #             if "description" in element:
            #                 element["description"] = re.sub(r"\n", "<br/>", element["description"])
            #             github = None
            #             if "links" in element:
            #                 for link in element["links"]:
            #                     if link["service"] == "github":
            #                         github = link
            #             element["github"] = github
            #             keywords = []
            #             if "keywords" in element:
            #                 for keyword in element["keywords"]:
            #                     if isinstance(keyword, str):
            #                         keyword = {"name": keyword}
            #                     keywords.append(keyword)
            #             element["keywords"] = keywords
            #     elif section["type"] == "skills":
            #         categories = []
            #         for category in section["contents"]:
            #             skills = []
            #             for skill in category["skills"]:
            #                 if isinstance(skill, str):
            #                     skill = {"name": skill}
            #                 skill["score"] = skill["score"] if "score" in skill else 50
            #                 skills.append(skill)

            #             proficient_skills = sorted([
            #                 skill for skill in skills if skill["score"] >= 70
            #             ], key=lambda skill: 100-skill["score"])
            #             non_proficient_skills = sorted([
            #                 skill
            #                 for skill in skills
            #                 if (skill["score"] < 70 and skill["score"] >= 10)
            #             ], key=lambda skill: 100-skill["score"])
            #             weak_skills = sorted([skill for skill in skills if skill["score"] < 10], key=lambda skill: 100-skill["score"])

            #             category["skills"] = proficient_skills + non_proficient_skills + weak_skills
            #             categories.append(category)
            #         section["contents"] = categories

            # self._data["sections"] = [
            #     section for section in self._data["sections"] if section["type"] != "none"
            # ]
            # self._data["sections"].sort(key=lambda section: section["priority"], reverse=True)

    def _get_section(self, name):
        try:
            if name in ("basics", "meta"):
                return self._data[name]
            return self.sections[name]
        except KeyError as e:
            msg = "Resume has no section '{name}'."
            raise KeyError(msg) from e

    def __getattr__(self, __name):
        # try:
        #     return super().__getattr__(self, name)
        # except AttributeError:
        #     return self._data[name]
        return self._get_section(__name)

    def __getitem__(self, __key: str) -> Any:
        return self._get_section(__key)

    @property
    def sections(self):
        return {key: ResumeSection(key, value) for key, value in self._data.items() if key in self._section_keys}

    @property
    def default_sections(self):
        return {key: ResumeSection(key, value) for key, value in self._data.items() if key in self._default_section_keys}

    @property
    def additional_sections(self):
        return {key: ResumeSection(key, value) for key, value in self._data.items() if key in self._additional_section_keys}

    def preprocess(self):
        pass

    def _pp_compute_age(self):
        try:
            birthdate = dt.datetime.strptime(
                self._data["basics"]["birthdate"],
                "%Y-%m-%d",
            ).astimezone("UTC")
            self._data["person"]["age"] = str(
                int((dt.datetime.now(tz="UTC") - birthdate).days / 365.25),
            )
        except ValueError:
            self._data["person"]["age"] = "Error"
        except KeyError:
            pass  # Birthdate not displayed.

    def render(self, template_name):
        template = env.get_template(template_name + ".html")
        with open(f"output/{re.sub(r'/', '_', self.name)}.html", "w") as output_file:
            output_file.write(template.render(self._data))


if __name__ == "__main__":
    resume = Resume(sys.argv[1])
    resume.render(sys.argv[2])
