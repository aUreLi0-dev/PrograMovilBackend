from .apis.curriculum import api as api_curriculum
from .apis.progress import api as api_progress
from .apis.simulation import api as api_simulation
from .apis.specialty import api as api_specialty

blueprints = [
    api_curriculum,
    api_progress,
    api_simulation,
    api_specialty,
]
