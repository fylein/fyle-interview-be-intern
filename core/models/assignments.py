import enum
from core import db
from core.apis.decorators import AuthPrincipal
from core.libs import helpers, assertions
from core.models.teachers import Teacher
from core.models.students import Student
from sqlalchemy.types import Enum as BaseEnum


class GradeEnum(str, enum.Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'


class AssignmentStateEnum(str, enum.Enum):
    DRAFT = 'DRAFT'
    SUBMITTED = 'SUBMITTED'
    GRADED = 'GRADED'


class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, db.Sequence('assignments_id_seq'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(Student.id), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(Teacher.id), nullable=True)
    content = db.Column(db.Text)
    grade = db.Column(BaseEnum(GradeEnum))
    state = db.Column(BaseEnum(AssignmentStateEnum), default=AssignmentStateEnum.DRAFT, nullable=False)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False, onupdate=helpers.get_utc_now)

    def __repr__(self):
        return '<Assignment %r>' % self.id

    @classmethod
    def filter(cls, *criterion):
        db_query = db.session.query(cls)
        return db_query.filter(*criterion)

    @classmethod
    def get_by_id(cls, _id):
        return cls.filter(cls.id == _id).first()

    @classmethod
    def upsert(cls, assignment_new: 'Assignment'):
        if assignment_new.id is not None:
            assignment = Assignment.get_by_id(assignment_new.id)
            assertions.assert_found(assignment, 'No assignment with this id was found')
            assertions.assert_valid(assignment.state == AssignmentStateEnum.DRAFT,
                                    'only assignment in draft state can be edited')

            assignment.content = assignment_new.content
        else:
            assignment = assignment_new
            db.session.add(assignment_new)

        db.session.flush()
        return assignment

    @classmethod
    def submit(cls, _id, teacher_id, auth_principal: AuthPrincipal):
        assignment = Assignment.get_by_id(_id)
        assertions.assert_found(assignment, 'No assignment with this id was found')
        assertions.assert_valid(assignment.student_id == auth_principal.student_id, 'This assignment belongs to some other student')
        assertions.assert_valid(assignment.content is not None, 'assignment with empty content cannot be submitted')
        assertions.assert_valid(assignment.state == AssignmentStateEnum.DRAFT,"only a draft assignment can be submitted")

        assignment.teacher_id = teacher_id
        assignment.state = AssignmentStateEnum.SUBMITTED
        db.session.flush()

        return assignment


    @classmethod
    def mark_grade(cls, _id, grade, auth_principal: AuthPrincipal):
        assignment = Assignment.get_by_id(_id)
        assertions.assert_found(assignment, 'No assignment with this id was found')
        assertions.assert_valid(grade is not None, 'assignment with empty grade cannot be graded')

        assertions.assert_valid(assignment.teacher_id == auth_principal.teacher_id,f"Assignment with id: {assignment.id} is not submitted to Teacher with teacher_id: {auth_principal.teacher_id}")
        # teacher cant regrade a assignment.
        assertions.assert_valid(assignment.state != AssignmentStateEnum.GRADED, f"Teacher cant regrade an assignment.")

        assignment.grade = grade
        assignment.state = AssignmentStateEnum.GRADED
        db.session.flush()

        return assignment

    @classmethod
    def get_assignments_by_student(cls, student_id):
        return cls.filter(cls.student_id == student_id).all()

    @classmethod
    def get_assignments_by_teacher(cls):
        return cls.query.all()

    @classmethod
    def get_assignments_by_principal(cls):
        return cls.filter(cls.state != AssignmentStateEnum.DRAFT).all()
    
    @classmethod
    def get_submitted_or_graded_assignments(cls):
        return cls.filter(cls.state in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]).all()
    
    @classmethod
    def regrade(cls, _id, grade):
        assignment = Assignment.get_by_id(_id)
        assertions.assert_found(assignment, f"No assignment with id: {_id} found.")
        assertions.assert_valid(
            grade is not None, 'assignment with empty grade cannot be graded')
        # principal can grade submitted assignments | regrade graded assignments only.
        assertions.assert_valid(assignment.state != AssignmentStateEnum.DRAFT, f"Principal cannot grade assignment in {assignment.state} state.")

        assignment.grade = grade

        # dont ve to change the state if already graded.
        if(assignment.state == AssignmentStateEnum.SUBMITTED):
            assignment.state = AssignmentStateEnum.GRADED
        
        db.session.flush()

        return assignment
