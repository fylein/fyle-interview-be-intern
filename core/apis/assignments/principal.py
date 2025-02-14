from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, Teacher

from .schema import AssignmentSchema, AssignmentGradeSchema, TeacherSchema

principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)


@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of assignments"""
    submitted_or_graded_assignment = Assignment.get_submitted_or_graded_assignments(
    )  # this is a python obj that we want to store persistently inside a db.
    principal_assignments_dump = AssignmentSchema().dump(
        submitted_or_graded_assignment, many=True)  # but before that we need to serialize it so that it could be sent over the wire.
    return APIResponse.respond(data=principal_assignments_dump)


# GET /principal/teachers
@principal_assignments_resources.route("/teachers", methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def get_teachers(p):
    """ Returns a list of  the Teachers. """
    teachers = Teacher.list_teachers()
    teachers_dump = TeacherSchema().dump(teachers, many=True)
    return APIResponse.respond(data=teachers_dump)


@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade an assignment"""
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)

    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p
    )
    db.session.commit()
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    return APIResponse.respond(data=graded_assignment_dump)
