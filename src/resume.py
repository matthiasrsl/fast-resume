import contextlib
import datetime as dt
import json
import locale
import logging
import logging.config
import re
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader

from src.constants import DEFAULT_SECTIONS
from src.resume_section import ResumeSection
from src.utils import Link, dotdict, escape_html

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger("fast-resume")

env = Environment(loader=FileSystemLoader("templates/"), autoescape=False)  # noqa: S701


class ResumeParsingError(Exception):
    pass


class Resume:
    def __init__(self, name):
        logger.debug("Creating Resume %s.", name)

        resume_file = Path(f"resumes/{name}")

        with resume_file.open() as file:
            raw_data = file.read()
            if resume_file.suffix == ".json":
                parsed_data = json.loads(raw_data)
            elif resume_file.suffix in (".yaml", ".yml"):
                parsed_data = yaml.safe_load(raw_data)
            else:
                msg = f"File extension '{resume_file.suffix}' not supported"
                raise ValueError(msg)

        self._data = dotdict(parsed_data)

        try:
            locale.setlocale(locale.LC_ALL, (self._data.meta.lang, "utf8"))
        except locale.Error as e:
            msg = f"Invalid language code : {self._data.meta.lang}. Maybe the locale is uninstalled on the system."
            raise ResumeParsingError(msg) from e
        else:
            self.lang = self._data.meta.lang

        self.date_format = self._data.meta.date_format
        self.name = resume_file.stem
        self._technical_sections_keys = set(self._data)
        self._section_keys = self._technical_sections_keys - {"basics", "meta"}
        self._additional_section_keys = self._section_keys - DEFAULT_SECTIONS
        self._default_section_keys = self._section_keys - self._additional_section_keys

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
        return {key: ResumeSection(key, value, self) for key, value in self._data.items() if key in self._section_keys}

    @property
    def default_sections(self):
        return {
            key: ResumeSection(key, value, self)
            for key, value in self._data.items()
            if key in self._default_section_keys
        }

    @property
    def additional_sections(self):
        return {
            key: ResumeSection(key, value, self)
            for key, value in self._data.items()
            if key in self._additional_section_keys
        }

    @property
    def main_sections(self):
        return [self.sections[section_key] for section_key in self.meta.main_sections]

    @property
    def aside_sections(self):
        return [self.sections[section_key] for section_key in self.meta.aside_sections]

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

    def render(self, template_name):
        template = env.get_template(template_name + ".html")
        output_path = Path(f"output/{re.sub(r'/', '_', self.name)}_{template_name}.html")
        with output_path.open("w") as output_file:
            output_file.write(template.render(resume=self))
        logger.info("Exported resume %s to %s.", self.name, output_path)
