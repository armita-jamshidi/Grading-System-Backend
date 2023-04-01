from flask_sqlalchemy import SQLAlchemy
import time

db = SQLAlchemy()
association_table_student = db.Table(
  "association1",
  db.Column("course_id", db.Integer, db.ForeignKey("course.id")),
  db.Column("student_id", db.Integer, db.ForeignKey("user.id"))
)

association_table_instructor = db.Table(
  "association2",
  db.Column("course_id", db.Integer, db.ForeignKey("course.id")),
  db.Column("instructor_id", db.Integer, db.ForeignKey("user.id"))
)


class Course(db.Model):
  """
  Course model
  """
  __tablename__ = "course"
  id = db.Column(db.Integer, primary_key = True, autoincrement=True)
  code = db.Column(db.String, nullable=False)
  name = db.Column(db.String, nullable=False)
  assignments = db.relationship("Assignment", cascade="delete")
  instructors = db.relationship("User", secondary=association_table_instructor, back_populates="instructor_courses")
  students = db.relationship("User", secondary=association_table_student, back_populates="student_courses")

  def __init__(self, **kwargs):
    """
    Initializes a course object
    """
    self.code = kwargs.get("code", "")
    self.name = kwargs.get("name", "")
   
  def serialize(self):
    """
    Serializes a course Object
    """
    return {"id": self.id, "code": self.code, "name": self.name, "students": [s.simple_serialize() for s in self.students],
            "instructors": [i.simple_serialize() for i in self.instructors],
            "assignments": [a.simple_serialize() for a in self.assignments]}
  
  def simple_serialize(self):
    """
    Simple serializes a course Object
    """
    return {"id": self.id, "code": self.code, "name": self.name}

class User(db.Model):
  """
  Users
  """
  __tablename__ = "user"
  id = db.Column(db.Integer, primary_key = True, autoincrement=True)
  name = db.Column(db.String, nullable=False)
  netid = db.Column(db.String, nullable=False)
  student_courses = db.relationship("Course", secondary=association_table_student, back_populates="students")
  instructor_courses = db.relationship("Course", secondary=association_table_instructor, back_populates="instructors")
  # courses = db.relationship("Course", secondary=association_table_student, back_populates="instructors")
  #secondary = """join(association1, association2, course_id=course_id).join(association1,association2.course_id==course_id)"""

  def __init__(self, **kwargs):
    """
    Initializes a user object
    """
    self.name = kwargs.get("name", "")
    self.netid = kwargs.get("netid", "")

  def get_both_courses(self):
    """
    Returns all the courses associated with this User
    """
    both_courses = []
    for c in self.student_courses:
      both_courses.append(c)
    for i in self.instructor_courses:
      both_courses.append(i)
    return both_courses
   
  def serialize(self):
    """
    Serializes a user object
    """
    both_courses = self.get_both_courses()
    return {"id": self.id, "name": self.name, "netid": self.netid, "courses":[c.serialize() for c in both_courses] }
  
  def simple_serialize(self):
    """
    Simple serializes a user object
    """
    return {"id": self.id, "name": self.name, "netid": self.netid}
  
  def simple_ser_two(self):
    """
    Serializes a user object, with courses
    """
    both_courses = self.get_both_courses()
    return {"id": self.id, "name": self.name, "netid": self.netid, "courses":[c.simple_serialize() for c in both_courses] }
  

  

class Assignment(db.Model):
    """
    Assignment
    """
    __tablename__ = "assignment"
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Integer, nullable=False)
    course = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

    def __init__(self, **kwargs):
      """
      Initializes an assignment object
      """
      self.title = kwargs.get("title", "")
      self.due_date = kwargs.get("due_date", "")
      self.course = kwargs.get("course")

    def serialize(self):
      """
      Serializes an assignment object
      """
      course_obj = Course.query.filter_by(id=self.course).first()
      return{
        "id": self.id,
        "title":self.title,
        "due_date": self.due_date,
        "course": course_obj.simple_serialize()
      }
    
    def simple_serialize(self):
      """
      Simple serialize an assignment object
      """
      course_obj = Course.query.filter_by(id=self.course).first()
      return{
        "id": self.id,
        "title":self.title,
        "due_date": self.due_date
      }
 



