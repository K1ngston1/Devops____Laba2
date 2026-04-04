from unittest.mock import patch, Mock, call

from . import service
from .models import Project
from .dto import (
    ProjectResponse,
    ProjectCreateRequest,
    ProjectCreateResponse,
    ProjectUpdateRequest,
    StudentAssignmentRequest,
)

PROJECT_RESPONSE = ProjectResponse(
    id=1,
    title="ML Course",
    syllabus_summary="Summary",
    description="Description",
    instructor_id=10,
    instructor_full_name="Jane Doe",
    instructor_email="jane@example.com",
    student_count=3,
    deadline="2026-06-01",
)


@patch("app.project.service.project_repo")
def test_get_project_by_id(mock_repo):
    project = Project(
        id=1,
        title="ML Course",
        syllabus_summary="Summary",
        description="Description",
        instructor_id=10,
        deadline="2026-06-01",
    )
    mock_repo.get_project_with_instructor_username.return_value = (project, "Jane Doe")
    mock_repo.get_user_email_by_id.return_value = "jane@example.com"
    mock_repo.get_project_student_count.return_value = 3

    db = Mock()

    result = service.get_project_by_id(1, db=db)

    mock_repo.get_project_with_instructor_username.assert_called_once_with(1, db=db)
    mock_repo.get_user_email_by_id.assert_called_once_with(10, db=db)
    mock_repo.get_project_student_count.assert_called_once_with(1, db=db)
    assert result == PROJECT_RESPONSE


@patch("app.project.service.project_repo")
def test_create_project(mock_repo):
    mock_repo.get_user_id_by_email.return_value = 10
    mock_repo.create_project.return_value = 1

    db = Mock()
    req = ProjectCreateRequest(
        title="ML Course",
        syllabus_summary="Summary",
        description="Description",
        instructor_email="jane@example.com",
        deadline="2026-06-01",
    )

    result = service.create_project(req, db=db)

    mock_repo.get_user_id_by_email.assert_called_once_with("jane@example.com", db=db)
    mock_repo.create_project.assert_called_once()
    assert result == ProjectCreateResponse(id=1)


@patch("app.project.service.project_repo")
def test_update_project(mock_repo):
    project = Project(
        id=1,
        title="ML Course Updated",
        syllabus_summary="Summary",
        description="Description",
        instructor_id=10,
        deadline="2026-06-01",
    )
    mock_repo.get_user_id_by_email.return_value = 10
    mock_repo.get_project_with_instructor_username.return_value = (project, "Jane Doe")
    mock_repo.get_user_email_by_id.return_value = "jane@example.com"
    mock_repo.get_project_student_count.return_value = 3

    db = Mock()
    req = ProjectUpdateRequest(
        title="ML Course Updated",
        syllabus_summary="Summary",
        description="Description",
        instructor_email="jane@example.com",
        deadline="2026-06-01",
    )

    result = service.update_project(1, req, db=db)

    mock_repo.get_user_id_by_email.assert_called_once_with("jane@example.com", db=db)
    mock_repo.update_project.assert_called_once()
    assert result.id == 1
    assert result.title == "ML Course Updated"


@patch("app.project.service.project_repo")
def test_assign_students_to_project(mock_repo):
    project = Project(
        id=1,
        title="ML Course",
        syllabus_summary="Summary",
        description="Description",
        instructor_id=10,
        deadline="2026-06-01",
    )
    mock_repo.get_user_id_by_email.side_effect = [20, 21]
    mock_repo.get_project_with_instructor_username.return_value = (project, "Jane Doe")
    mock_repo.get_user_email_by_id.return_value = "jane@example.com"
    mock_repo.get_project_student_count.return_value = 2

    db = Mock()
    req = StudentAssignmentRequest(
        student_emails=["alice@example.com", "bob@example.com"]
    )

    result = service.assign_students_to_project(1, req, db=db)

    mock_repo.get_user_id_by_email.assert_has_calls(
        [
            call("alice@example.com", db=db),
            call("bob@example.com", db=db),
        ]
    )
    mock_repo.assign_students_to_project.assert_called_once_with(1, [20, 21], db=db)
    assert result.id == 1
