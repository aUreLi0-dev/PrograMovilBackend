from .apis.assessment_type import api as api_assessment_type
from .apis.assessment import api as api_assessment
from .apis.student_score import api as api_student_score
from .apis.calculator import api as api_calculator
from .apis.career_setup import api as api_career_setup
from .apis.schedule import api as api_schedule

blueprints = [
    api_assessment_type,
    api_assessment,
    api_student_score,
    api_calculator,
    api_career_setup,
    api_schedule,
]
