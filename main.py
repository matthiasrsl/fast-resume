import json
import datetime as dt
import re
import sys

from jinja2 import Template, Environment, FileSystemLoader
from jinja2.exceptions import TemplateSyntaxError

env = Environment(loader=FileSystemLoader("templates/"))

services = {
    "linkedin": ("linkedin.com/in/", "https://linkedin.com/in/"),
    "github": ("github.com/", "https://github.com/"),
    "twitter": ("twitter.com/", "https://twitter.com/"),
    "instagram": ("instagram.com/ ", "https://instagram.com/"),
}


class Resume:
    def __init__(self, name):
        with open(f"resumes/{name}.json", "r") as file:
            raw_data = file.read()
            self.data = json.loads(raw_data)
            self.name = name
            try:
                birthdate = dt.datetime.strptime(
                    self.data["person"]["birthdate"], "%Y-%m-%d"
                )
                self.data["person"]["age"] = str(
                    int((dt.datetime.now() - birthdate).days / 365.25)
                )
            except ValueError:
                self.data["person"]["age"] = "Error"
            except KeyError:
                pass  # Birthdate not displayed.

            for i, account in enumerate(self.data["person"]["usernames"]):
                if account["service"] in services:
                    self.data["person"]["usernames"][i]["link"] = (
                        services[account["service"]][1] + account["username"]
                    )

            experiences = []
            for experience in self.data["experience"]:
                keywords = []
                if "keywords" in experience:
                    for keyword in experience["keywords"]:
                        if isinstance(keyword, str):
                            keyword = {"name": keyword}
                        keywords.append(keyword)
                experience["keywords"] = keywords
                experiences.append(experience)
            self.data["experience"] = experiences

            for acc in self.data["accomplishements"]:
                acc["description"] = re.sub(r"\n", "<br/>", acc["description"])
                github = None
                for link in acc["links"]:
                    if link["service"] == "github":
                        github = link
                acc["github"] = github
                keywords = []
                if "keywords" in acc:
                    for keyword in acc["keywords"]:
                        if isinstance(keyword, str):
                            keyword = {"name": keyword}
                        keywords.append(keyword)
                acc["keywords"] = keywords


            skills = []
            for skill in self.data["skills"]:
                if isinstance(skill, str):
                    skill = {"name": skill}
                skill["score"] = skill["score"] if "score" in skill else 50
                skills.append(skill)

            proficient_skills = [
                skill for skill in skills if skill["score"] >= 70
            ]
            non_proficient_skills = [
                skill
                for skill in skills
                if (skill["score"] < 70 and skill["score"] >= 10)
            ]
            weak_skills = [skill for skill in skills if skill["score"] < 10]
            self.data["skills"] = proficient_skills + non_proficient_skills + weak_skills

    def render(self, template_name):
        template = env.get_template(template_name + ".html")
        with open(f"output/{self.name}.html", "w") as output_file:
            output_file.write(template.render(self.data))


def debug(instruction):
    try:
        exec(instruction)
    except TemplateSyntaxError as e:
        print(f"{e.lineno}: {e.message}")


if __name__ == "__main__":
    resume = Resume(sys.argv[1])
    resume.render(sys.argv[2])