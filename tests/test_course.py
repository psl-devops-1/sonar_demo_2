import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_course_service(mocker):
    """Mocks CourseService methods used in courseBp."""
    return mocker.patch("controllers.courseController.courseService")


def test_list_courses_json(client, mocker, mock_course_service):
    """Test retrieving course list via JSON request."""
    mocker.patch("config.auth.loginRequired", lambda f: f)

    course_mock = MagicMock()
    course_mock.toDict.return_value = {"id": 1, "course_name": "Python 101", "description": "Intro course"}
    mock_course_service.getAllCourses.return_value = [course_mock]

    response = client.get("/courses", headers={"Accept": "application/json"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert len(data["courses"]) == 1
    assert data["courses"][0]["course_name"] == "Python 101"


def test_get_course_not_found_json(client, mocker, mock_course_service):
    """Test fetching non-existent course returns 404 JSON."""
    mocker.patch("config.auth.loginRequired", lambda f: f)
    mock_course_service.getCourseById.side_effect = ValueError("Course with ID 99 not found")

    response = client.get("/courses/99", headers={"Accept": "application/json"})

    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert "not found" in data["message"]


def test_create_course_success_json(client, mocker, mock_course_service):
    """Test successful course creation via JSON API."""
    mocker.patch("config.auth.roleRequired", lambda role: lambda f: f)

    mock_course = MagicMock()
    mock_course.course_name = "Flask Web Development"
    mock_course.toDict.return_value = {"id": 2, "course_name": "Flask Web Development", "description": "Learn Flask"}
    mock_course_service.createCourse.return_value = mock_course

    payload = {
        "courseName": "Flask Web Development",
        "description": "Comprehensive guide to Flask web application development."
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = client.post("/courses/create", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["course"]["id"] == 2


def test_create_course_validation_failure(client, mocker):
    """Test course creation fails when form payload is invalid."""
    mocker.patch("config.auth.roleRequired", lambda role: lambda f: f)

    payload = {
        "courseName": "Py",  # Too short (min length 3)
        "description": "Short"  # Too short (min length 10)
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = client.post("/courses/create", json=payload, headers=headers)

    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "courseName" in data["errors"]
    assert "description" in data["errors"]


def test_delete_course_success_json(client, mocker, mock_course_service):
    """Test deleting a course successfully."""
    mocker.patch("config.auth.roleRequired", lambda role: lambda f: f)
    mock_course_service.deleteCourse.return_value = None

    headers = {"Accept": "application/json"}
    response = client.post("/courses/1/delete", headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["message"] == "Course deleted successfully"