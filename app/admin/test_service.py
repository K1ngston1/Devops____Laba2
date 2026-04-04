from unittest.mock import patch, Mock

from . import service


def _make_mock_repo_for_load_test():
    """Return auth_repo and project_repo mocks wired up for create_load_test_data."""
    mock_auth_repo = Mock()
    mock_project_repo = Mock()

    # Return unique IDs for each created user/project
    mock_auth_repo.create_user.side_effect = list(
        range(1, 101)
    )  # 80 students + 20 instructors
    mock_project_repo.create_project.side_effect = list(range(1, 31))  # 30 projects

    return mock_auth_repo, mock_project_repo


@patch("app.admin.service.project_repo")
@patch("app.admin.service.auth_repo")
def test_create_load_test_data_counts(mock_auth_repo, mock_project_repo):
    mock_auth_repo.create_user.side_effect = list(range(1, 101))
    mock_project_repo.create_project.side_effect = list(range(1, 31))

    result = service.create_load_test_data(db=Mock())

    assert len(result.students) == 80
    assert len(result.instructors) == 20
    assert len(result.projects) == 30


@patch("app.admin.service.project_repo")
@patch("app.admin.service.auth_repo")
def test_create_load_test_data_student_emails(mock_auth_repo, mock_project_repo):
    mock_auth_repo.create_user.side_effect = list(range(1, 101))
    mock_project_repo.create_project.side_effect = list(range(1, 31))

    result = service.create_load_test_data(db=Mock())

    for student in result.students:
        assert student.email.endswith("@hmp.test"), (
            f"Student email {student.email!r} does not use @hmp.test domain"
        )


@patch("app.admin.service.project_repo")
@patch("app.admin.service.auth_repo")
def test_create_load_test_data_instructor_emails(mock_auth_repo, mock_project_repo):
    mock_auth_repo.create_user.side_effect = list(range(1, 101))
    mock_project_repo.create_project.side_effect = list(range(1, 31))

    result = service.create_load_test_data(db=Mock())

    for instructor in result.instructors:
        assert instructor.email.endswith("@hmp.test"), (
            f"Instructor email {instructor.email!r} does not use @hmp.test domain"
        )


@patch("app.admin.service.project_repo")
@patch("app.admin.service.auth_repo")
def test_create_load_test_data_project_title_prefix(mock_auth_repo, mock_project_repo):
    mock_auth_repo.create_user.side_effect = list(range(1, 101))
    mock_project_repo.create_project.side_effect = list(range(1, 31))

    result = service.create_load_test_data(db=Mock())

    for project in result.projects:
        assert project.title.startswith("$TEST$"), (
            f"Project title {project.title!r} does not start with $TEST$ prefix"
        )


@patch("app.admin.service.project_repo")
@patch("app.admin.service.auth_repo")
def test_create_load_test_data_each_student_has_at_least_3_projects(
    mock_auth_repo, mock_project_repo
):
    mock_auth_repo.create_user.side_effect = list(range(1, 101))
    mock_project_repo.create_project.side_effect = list(range(1, 31))

    result = service.create_load_test_data(db=Mock())

    for student in result.students:
        assert len(student.project_ids) >= 3, (
            f"Student {student.email!r} is assigned to only {len(student.project_ids)} project(s)"
        )
