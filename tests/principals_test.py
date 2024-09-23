from core.models.assignments import AssignmentStateEnum, GradeEnum
from flask import jsonify
from core.libs.exceptions import FyleError
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError
import pytest
from core import app
from core.libs import helpers
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import BadRequest, InternalServerError
from core.models.teachers import Teacher
from core.models.assignments import Assignment
from core.apis.responses import APIResponse


def test_get_assignments(client, h_principal):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


def test_grade_assignment_draft_assignment(client, h_principal):
    """
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 156,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 400


def test_grade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.C.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C


def test_regrade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B


# Test case for missing required fields in grade_assignment
def test_grade_assignment_missing_fields(client, h_principal):
    response = client.post('/principal/assignments/grade', json={}, headers=h_principal)

    assert response.status_code == 400
    assert response.json['error'] == 'Missing required fields: id or grade'

# Test case for missing 'id' field
def test_grade_assignment_missing_id(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={'grade': 'A'},
        headers=h_principal
    )

    assert response.status_code == 400
    assert response.json['error'] == 'Missing required fields: id or grade'

# Test case for missing 'grade' field
def test_grade_assignment_missing_grade(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={'id': 4},
        headers=h_principal
    )

    assert response.status_code == 400
    assert response.json['error'] == 'Missing required fields: id or grade'