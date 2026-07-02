from .apis.advising import api as api_advising
from .apis.announcement import api as api_announcement
from .apis.contact import api as api_contact
from .apis.section import api as api_section

blueprints = [
    api_section,
    api_announcement,
    api_advising,
    api_contact,
]
