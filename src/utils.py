import html
from urllib.parse import urlparse

from src.constants import DOMAIN_SERVICE_MAPPING


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


def escape_html(obj: dict | list | str):
    if isinstance(obj, str):
        return html.escape(obj, quote=False)

    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = escape_html(value)
    elif isinstance(obj, list):
        for i, elt in enumerate(obj):
            obj[i] = escape_html(elt)
    return obj

class Link:
    def __init__(self, url: str):
        self.url = url
        parsed_url = urlparse(url)
        if parsed_url.scheme in ("http", "https"):
            self.domain = ".".join(parsed_url.hostname.split(".")[-2:])
            self.short_url = parsed_url.hostname + parsed_url.path
            try:
                self.identifier = DOMAIN_SERVICE_MAPPING[self.domain][0]
                self.name = DOMAIN_SERVICE_MAPPING[self.domain][1]
            except KeyError:
                self.identifier = "web"
                self.name = "Website"
        elif parsed_url.scheme == "mailto":
            self.domain = ""
            self.short_url = parsed_url.path
            self.identifier = "mail"
            self.name = "E-mail"
        else:
            msg = "A link's URL scheme must be either HTTP, HTTPS or mailto."
            raise ValueError(msg)
