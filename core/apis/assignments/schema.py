from marshmallow import Schema, EXCLUDE, fields, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_enum import EnumField
from core.models.assignments import Assignment, GradeEnum, Teacher
from core.libs.helpers import GeneralObject


class AssignmentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Assignment
        unknown = EXCLUDE

    id = auto_field(required=False, allow_none=True)
    content = auto_field()
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    teacher_id = auto_field(dump_only=True)
    student_id = auto_field(dump_only=True)
    grade = auto_field(dump_only=True)
    state = auto_field(dump_only=True)

    @post_load
    def initiate_class(self, data_dict, many, partial):
        # pylint: disable=unused-argument,no-self-use
        return Assignment(**data_dict)


class AssignmentSubmitSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Integer(required=True, allow_none=False)
    teacher_id = fields.Integer(required=True, allow_none=False)

    @post_load
    def initiate_class(self, data_dict, many, partial):
        # pylint: disable=unused-argument,no-self-use
        return GeneralObject(**data_dict)


class AssignmentGradeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Integer(required=True, allow_none=False)
    grade = EnumField(GradeEnum, required=True, allow_none=False)

    @post_load
    def initiate_class(self, data_dict, many, partial):
        # pylint: disable=unused-argument,no-self-use
        return GeneralObject(**data_dict)

class TeacherSchema(SQLAlchemyAutoSchema):
    # this is the pragma | directive thing that we ve got to instruct marshmallow-sqlalchemy for config purpose.
    class Meta:
        # let em know what model to use to generate the auto schema.
        model = Teacher
        # exclude all them unknown pros and dont raise an error for that thing.
        unknown = EXCLUDE

    id = auto_field(allow_none=False, required=True) # being consistent with the table attrs.
    user_id = auto_field()
    # dont want to update those fields while deserialzing.
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)

    """  this method is ivked when we got to deserialize. many repr that we're going to ve multiple dicts | dicts[]. partial is used to flag the checkpoint that we're going to create the obj from scratch or only some of them. dump_only kicks right in here. """
    @post_load
    def initiate_class(self, data_dict, many, partial):
        return GeneralObject(**data_dict)
