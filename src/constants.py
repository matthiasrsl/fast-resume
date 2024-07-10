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
        "label": "area",
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

L10N = {
    "en": {
        "date_since": "Since",
        "date_until": "Until",
    },
    "fr": {
        "date_since": "Depuis",
        "date_until": "Jusqu'à",
    },
}

SECTION_NAME_L10N = {
    "en": {
        "work": "Work experience",
        "volunteer": "Volunteer",
        "education": "Education",
        "awards": "Awards",
        "certificates": "Certificates",
        "publications": "Publications",
        "skills": "Skills",
        "languages": "Languages",
        "interests": "Personal interests",
        "references": "References",
        "projects": "Personal projects",
    },
    "fr": {
        "work": "Expérience",
        "volunteer": "Volontariat",
        "education": "Formation",
        "awards": "Récompenses",
        "certificates": "Certifications",
        "publications": "Publications",
        "skills": "Compétences",
        "languages": "Langues",
        "interests": "Centres d'intérêt",
        "references": "Références",
        "projects": "Projets personnels",
    },
}

DOMAIN_SERVICE_MAPPING = {
    "twitter.com": ("twitter", "Twitter"),
    "github.com": ("github", "GitHub"),
    "linkedin.com": ("linkedin", "LinkedIn"),
    "instagram.com": ("instagram", "Instagram"),
}
