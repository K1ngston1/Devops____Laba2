import pytest
from unittest.mock import patch, Mock

from . import service


@patch("app.submission.service.repository")
def test_create_submission_success(mock_repository):
    mock_repository.get_project_student.return_value = 42
    mock_repository.insert_submission.return_value = 100

    db = Mock()

    submission_id = service.create_submission(
        project_id=1,
        student_id=2,
        title="Test",
        encrypted_content=b"data",
        db=db,
    )

    mock_repository.get_project_student.assert_called_once_with(2, 1, db=db)
    mock_repository.insert_submission.assert_called_once()
    assert submission_id == 100


@patch("app.submission.service.repository")
def test_create_submission_student_not_found(mock_repository):
    mock_repository.get_project_student.return_value = None

    db = Mock()

    with pytest.raises(service.SubmissionError):
        _ = service.create_submission(
            project_id=1,
            student_id=2,
            title="Test",
            encrypted_content=b"data",
            db=db,
        )

    mock_repository.get_project_student.assert_called_once_with(2, 1, db=db)
    mock_repository.insert_submission.assert_not_called()


@patch("app.submission.service.repository")
def test_remove_submission(mock_repository):
    db = Mock()

    service.remove_submission(submission_id=5, db=db)

    mock_repository.delete_submission.assert_called_once_with(5, db=db)


@patch("app.submission.service.repository")
def test_list_submissions_for_ui(mock_repository):
    expected = [{"id": 1, "title": "Paper"}]
    mock_repository.get_submissions_for_ui.return_value = expected

    db = Mock()

    result = service.list_submissions_for_ui(db=db)

    mock_repository.get_submissions_for_ui.assert_called_once_with(db=db)
    assert result == expected


@patch("app.submission.service.repository")
def test_get_submission_hash(mock_repository):
    mock_repository.get_submission_content_hash.return_value = "abc123"

    db = Mock()

    result = service.get_submission_hash(submission_id=7, db=db)

    mock_repository.get_submission_content_hash.assert_called_once_with(7, db=db)
    assert result == "abc123"


@patch("app.submission.service.repository")
def test_get_submission_content(mock_repository):
    mock_repository.get_submission_content.return_value = b"encrypted"

    db = Mock()

    result = service.get_submission_content(submission_id=3, db=db)

    mock_repository.get_submission_content.assert_called_once_with(3, db=db)
    assert result == b"encrypted"


@patch("app.submission.service.repository")
def test_get_instructor_key_returns_base64(mock_repository):
    mock_repository.get_instructor_public_key.return_value = b"\x00\x01\x02"

    db = Mock()

    result = service.get_instructor_key(project_id="1", db=db)

    mock_repository.get_instructor_public_key.assert_called_once_with("1", db=db)
    assert result == "AAEC"
