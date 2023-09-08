import datetime as dt
import json
import logging
import logging.config
import re
from pathlib import Path
from typing import Any

import markdown
from jinja2 import Environment, FileSystemLoader

from src.constants import DEFAULT_SECTIONS
from src.resume_section import ResumeSection
from src.utils import Link, dotdict, escape_html
import contextlib

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger("LightCvMaker")

env = Environment(loader=FileSystemLoader("templates/"), autoescape=True)


class Resume:
    def __init__(self, name):
        logger.debug("Creating Resume %s.", name)
        with Path(f"resumes/{name}.json").open() as file:
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

    def __iter__(self):
        return iter(self.sections.values())

    @property
    def sections(self):
        return {key: ResumeSection(key, value) for key, value in self._data.items() if key in self._section_keys}

    @property
    def default_sections(self):
        return {
            key: ResumeSection(key, value)
            for key, value in self._data.items()
            if key in self._default_section_keys
        }

    @property
    def additional_sections(self):
        return {
            key: ResumeSection(key, value)
            for key, value in self._data.items()
            if key in self._additional_section_keys
        }

    def preprocess(self):
        self._preprocess_age()
        self._preprocess_dates()
        self._preprocess_links()
        self._preprocess_text_fields()

    def _preprocess_age(self):
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

    def _preprocess_dates(self):
        for section in self:
            for element in section:
                with contextlib.suppress(TypeError):
                    element.startDate = dt.datetime.strptime(element.startDate, "%Y-%m-%d").astimezone(None)
                    element.endDate = dt.datetime.strptime(element.endDate, "%Y-%m-%d").astimezone(None)

    def _preprocess_links(self):
        for section in self:
            for element in section:
                element.link = Link(element.url) if element.url else None

    def _preprocess_text_fields(self):
        escape_html(self._data)

        for section in self.sections.values():
            for element in section:
                if isinstance(element.summary, str):
                    element.summary = markdown.markdown(element.summary.replace("\n", "<br/>"))


    def render(self, template_name):
        template = env.get_template(template_name + ".html")
        with Path(f"output/{re.sub(r'/', '_', self.name)}.html").open("w") as output_file:
            output_file.write(template.render(resume=self))
