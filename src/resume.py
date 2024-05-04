import contextlib
import datetime as dt
import json
import locale
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

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger("LightCvMaker")

env = Environment(loader=FileSystemLoader("templates/"), autoescape=False)  # noqa: S701


class ResumeParsingError(Exception):
    pass


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

        try:
            locale.setlocale(locale.LC_ALL, (self._data.meta.language, "utf8"))
        except locale.Error as e:
            msg = f"Invalid language code : {self._data.meta.language}. Maybe the locale is uninstalled on the system."
            raise ResumeParsingError(msg) from e

        if self._data.meta.date_format is None:
            self._data.meta.date_format = "%x"

    def _get_section(self, name):
        try:
            if name in ("basics", "meta"):
                return self._data[name]
            return self.sections[name]
        except KeyError as e:
            msg = f"Resume has no section '{name}'."
            raise KeyError(msg) from e

    def __getattr__(self, __name):
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
            key: ResumeSection(key, value) for key, value in self._data.items() if key in self._default_section_keys
        }

    @property
    def additional_sections(self):
        return {
            key: ResumeSection(key, value) for key, value in self._data.items() if key in self._additional_section_keys
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
