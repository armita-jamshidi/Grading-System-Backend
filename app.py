from db import db
import json
from flask import Flask, request

from db import Course
from db import User
from db import Assignment

app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


def success_response(data, code=200):
    """
    Success response
    """
    return json.dumps(data), code

def failure_response(message, code=400):
    """
    Failure response
    """
    return json.dumps({"error": message}), code

# your routes here
@app.route("/api/courses/")
def get_courses():
    """
    Endpoint for getting all courses
    """
    courses = [course.serialize() for course in Course.query.all()]
    return success_response({"courses":courses})

@app.route("/api/courses/", methods = ["POST"])
def create_course():
    """
    Endpoint for creating a new course
    """
    body = json.loads(request.data)
    code = body.get("code")
    name = body.get("name")
    if code is None or name is None:
        return failure_response("missing a field")
    new_course = Course(code = body.get("code"),
                        name = body.get("name"))
    db.session.add(new_course)
    db.session.commit()
    return success_response(new_course.serialize(),201)

@app.route("/api/courses/<int:course_id>/")
def get_course_by_id(course_id):
    """
    Endpoint for getting a course
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response(("Course not found!"), 404)
    return success_response(course.serialize())

@app.route("/api/courses/<int:id>/", methods = ["DELETE"])
def delete_course(id):
    """
    Endpoint for deleting a course by id
    """
    course = Course.query.filter_by(id = id).first()
    if course is None:
        return failure_response(("Course not found!"), 404)
    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize())

@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a user
    """
    body = json.loads(request.data)
    name = body.get("name")
    netid = body.get("netid")
    if name is None or netid is None:
        return failure_response("missing a field")
    new_user = User(name = body.get("name"),
                        netid = body.get("netid"))
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(),201)


@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting a user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response(("User not found!"), 404)
    return success_response(user.simple_ser_two())

@app.route("/api/courses/<int:course_id>/add/", methods=["POST"])
def add_user_to_course(course_id):
    """
    Endpoint for adding user to a course
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response(("Course not found!"), 404)

    body = json.loads(request.data)
    user_id = body.get("user_id")
    type = body.get("type")

    if type != "student" and type != "instructor":
        return failure_response("Type is invalid")
    
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response(("User not found!"), 404)
        

    course.instructors.append(user)
    # if type == "student":
    #     course.students.append(user)
    # elif type == "instructor":
    #     course.instructors.append(user)
    
    #user.courses.append(course)
    db.session.commit()
    return success_response(course.serialize())

@app.route("/api/courses/<int:course_id>/assignment/", methods=["POST"])
def create_assignment(course_id):
    """
    Endpoint for creating an assignment
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response(("Course not found!"), 404)

    body = json.loads(request.data)
    t = body.get("title")
    d = body.get("due_date")

    if t is None or d is None:
        return failure_response("Missing field!")

    assignment = Assignment(
        title = body.get("title"),
        due_date = body.get("due_date"),
        course = course_id
    )

    db.session.add(assignment)
    db.session.commit()
    return success_response(assignment.serialize(), 201)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
