import pytest
from assignment0.main import main


@pytest.fixture
def mock_object(mocker):
    return mocker.Mock()


def test_main(mocker, mock_object):
    # Mocks
    delete_func = mocker.patch("assignment0.delete_existing_db", return_value=True)
    incident_data = mocker.patch("assignment0.fetch_incidents", return_vale=mock_object)
    incidents = mocker.patch("assignment0.extract_incidents", return_value=mock_object)
    db = mocker.patch("assignment0.create_db", return_value=mock_object)
    mock_populate_func = mocker.patch("assignment0.populate_db", return_value=True)
    mock_print_rec_func = mocker.patch("assignment0.print_record", return_value=True)
    mock_status_func = mocker.patch("assignment0.status", return_value=True)

    # Execute
    url = "http://testurl.com"
    main(url)

    # Asserts
    delete_func.assert_called_once()
    incident_data.assert_called_once()
    incidents.assert_called_once()
    db.assert_called_once()
    mock_populate_func.assert_called_once()
    mock_status_func.assert_called_once()
