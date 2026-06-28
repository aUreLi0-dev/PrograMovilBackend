from .apis.assessment_type import api as api_assessment_type
from .apis.assessment import api as api_assessment
from .apis.student_score import api as api_student_score
from .apis.calculator import api as api_calculator

blueprints = [
    api_assessment_type,
    api_assessment,
    api_student_score,
    api_calculator,
]
