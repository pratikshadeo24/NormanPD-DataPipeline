import os
import pytest
from assignment0 import assignment
from tests import result_page_0, result_random_page, result_last_page


def get_file_content(file_name):
    """Extract test data file contents"""
    base_dir = os.getcwd()
    file_path = f"{base_dir}/tests/{file_name}"
    try:
        with open(file_path, "r") as file:
            file_contents = file.read()
            return file_contents
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as ex:
        print(f"ERROR in reading file '{file_name}': {ex}")
    return None


@pytest.fixture
def mock_cwd(mocker):
    curr_work_dir = mocker.patch("os.getcwd", return_value="/test/mock")
    return curr_work_dir


@pytest.fixture
def sample_url():
    """Sample URL for mock request"""
    return "http://testurl.com"


@pytest.fixture
def mock_object(mocker):
    """Mock class object"""
    return mocker.Mock()


@pytest.fixture
def sample_page0():
    """Sample first page content in string"""
    file_name = "data/page0.txt"
    page_content = get_file_content(file_name)
    return page_content


@pytest.fixture
def sample_random_page():
    """Sample random page content in string other than first and last pages"""
    file_name = "data/random_page.txt"
    page_content = get_file_content(file_name)
    return page_content


@pytest.fixture
def sample_last_page():
    """Sample last page content in string"""
    file_name = "data/last_page.txt"
    page_content = get_file_content(file_name)
    return page_content


@pytest.fixture
def sample_page_text():
    """Sample page text"""
    return [
        "1/1/2024 23:14 2024-00000215 4741 N PORTER AVE Traffic Stop OK0140200",
        "1/1/2024 23:17 2024-00000062 2000 ANN BRANDEN BLVD Transfer/Interfacility EMSSTAT",
        "1/1/2024 23:38 2024-00000218 1028 LESLIE LN 911 Call Nature Unknown OK0140200",
    ]


@pytest.fixture
def mock_sqlite(mocker):
    return mocker.patch('assignment0.assignment.sqlite3.connect')


@pytest.fixture
def expected_incidents():
    """Sample extracted incidents with defined fields"""
    return [
        {
            "incident_time": "23:14",
            "incident_number": "2024-00000215",
            "incident_location": "4741 N PORTER AVE",
            "incident_nature": "Traffic Stop",
            "incident_ori": "OK0140200",
        },
        {
            "incident_time": "23:17",
            "incident_number": "2024-00000062",
            "incident_location": "2000 ANN BRANDEN BLVD",
            "incident_nature": "Transfer/Interfacility",
            "incident_ori": "EMSSTAT",
        },
        {
            "incident_time": "23:38",
            "incident_number": "2024-00000218",
            "incident_location": "1028 LESLIE LN",
            "incident_nature": "911 Call Nature Unknown",
            "incident_ori": "OK0140200",
        },
    ]


def test_delete_existing_db_file_exists(mocker, mock_cwd):
    """Test deletion of existing database file"""
    # Mocks
    mock_check_path = mocker.patch("os.path.exists", return_value=True)
    mocked_remove = mocker.patch("os.remove")

    # Execute
    db_name = "test.db"
    assignment.delete_existing_db(db_name)

    # Asserts
    mock_cwd.assert_called_once()
    mock_check_path.assert_called_once_with("/test/mock/resources/test.db")
    mocked_remove.assert_called_once_with("/test/mock/resources/test.db")


def test_delete_existing_db_file_does_not_exist(mocker, mock_cwd):
    """Test deletion of database file if it doesn't exist"""
    # Mocks
    mock_check_path = mocker.patch("os.path.exists", return_value=False)
    mocked_remove = mocker.patch("os.remove")

    # Execute
    db_name = "test.db"
    assignment.delete_existing_db(db_name)

    # Asserts
    mock_cwd.assert_called_once()
    mock_check_path.assert_called_once_with("/test/mock/resources/test.db")
    mocked_remove.assert_not_called()


def test_delete_existing_db_failure(mocker, mock_cwd):
    """Test deletion of database file if exception occurs"""
    # Mocks
    mock_check_path = mocker.patch("os.path.exists", side_effect=Exception("Test exception"))
    mocked_remove = mocker.patch("os.remove")

    # Execute
    db_name = "test.db"
    assignment.delete_existing_db(db_name)

    # Asserts
    mock_cwd.assert_called_once()
    mock_check_path.assert_called_once_with("/test/mock/resources/test.db")
    mocked_remove.assert_not_called()


def test_fetch_incidents_success(mocker, sample_url):
    """Test successful fetching of PDF file data"""
    # Mocks
    mock_data = b"test response data"
    request = mocker.patch(
        "urllib.request.urlopen", return_value=mocker.Mock(read=lambda: mock_data)
    )

    # Execute
    data = assignment.fetch_incidents(sample_url)

    # Asserts
    request.assert_called_once()
    assert data == mock_data


def test_fetch_incidents_failure(mocker, sample_url):
    """Test exception while fetching of PDF file data"""
    # Mocks
    request = mocker.patch(
        "urllib.request.urlopen", side_effect=Exception("Test exception")
    )

    # Execute
    data = assignment.fetch_incidents(sample_url)

    # Asserts
    request.assert_called_once()
    assert data is None


def test_extract_incidents(mocker, mock_object, sample_page_text, expected_incidents):
    """Test extracted incidents from PDF file data"""
    # Mocks
    reader = mock_object
    reader.pages = [mock_object]
    sample_incident_data = mock_object
    mocker.patch("assignment0.assignment.io.BytesIO", return_vale=mock_object)
    mocker.patch("assignment0.assignment.PdfReader", return_value=reader)
    mocker.patch("assignment0.assignment.extract_page_text", return_value=sample_page_text)

    # Execute
    incidents = assignment.extract_incidents(sample_incident_data)

    # Asserts
    assert incidents[0] == expected_incidents[0]
    assert incidents[1] == expected_incidents[1]
    assert incidents[2] == expected_incidents[2]


def test_extract_page_text_page0(mock_object, sample_page0):
    """Test extracted first page content"""
    # Mocks
    mock_page = mock_object
    mock_page.extract_text.return_value = sample_page0

    # Execute
    page_text = assignment.extract_page_text(mock_page, 0, 5)

    # Asserts
    assert page_text[0] == result_page_0[0]
    assert page_text[6] == result_page_0[6]
    assert page_text[-1] == result_page_0[-1]


def test_extract_page_text_random_page(mock_object, sample_random_page):
    """Test extracted random page content"""
    # Mocks
    mock_page = mock_object
    mock_page.extract_text.return_value = sample_random_page

    # Execute
    page_text = assignment.extract_page_text(mock_page, 2, 5)

    # Asserts
    assert page_text[0] == result_random_page[0]
    assert page_text[6] == result_random_page[6]
    assert page_text[-1] == result_random_page[-1]


def test_extract_page_text_last_page(mock_object, sample_last_page):
    """Test extracted last page content"""
    # Mocks
    mock_page = mock_object
    mock_page.extract_text.return_value = sample_last_page

    # Execute
    page_text = assignment.extract_page_text(mock_page, 4, 5)

    # Asserts
    assert page_text[0] == result_last_page[0]
    assert page_text[6] == result_last_page[6]
    assert page_text[-1] == result_last_page[-1]


def test_split_all_incidents(sample_random_page):
    # Execute
    extracted_incidents = assignment.split_all_incidents(sample_random_page)

    # Asserts
    assert extracted_incidents[0] == result_random_page[0]
    assert extracted_incidents[6] == result_random_page[6]
    assert extracted_incidents[-1] == result_random_page[-1]


def test_split_all_incidents_last_page(sample_last_page):
    # Execute
    extracted_incidents = assignment.split_all_incidents(sample_last_page, 'last')

    # Asserts
    assert extracted_incidents[0] == result_last_page[0]
    assert extracted_incidents[6] == result_last_page[6]
    assert extracted_incidents[-1] == result_last_page[-1]


def test_refactor_page_data(sample_page_text, expected_incidents):
    """Test refactoring of page content to get required fields"""
    # Execute
    page_incidents = assignment.refactor_page_data(sample_page_text)

    # Asserts
    assert len(page_incidents) == 3
    assert (
        page_incidents[0]["incident_location"]
        == expected_incidents[0]["incident_location"]
    )
    assert (
        page_incidents[1]["incident_nature"] == expected_incidents[1]["incident_nature"]
    )
    assert (
        page_incidents[2]["incident_number"] == expected_incidents[2]["incident_number"]
    )


def test_extract_location_and_nature_case1():
    """Test extract location and nature if no numeric is in the beginning of incident nature"""
    # Initialize
    record = ["226", "CINDY", "AVE", "Chest", "Pain"]

    # Execute
    location, nature = assignment.extract_location_and_nature(record)

    # Asserts
    assert location == "226 CINDY AVE"
    assert nature == "Chest Pain"


def test_extract_location_and_nature_case2():
    """Test extract location and nature if numeric is in the beginning of incident nature"""
    # Initialize
    record = ["2900", "CHAUTAUQUA", "AVE", "911", "Call", "Nature", "Unknown"]

    # Execute
    location, nature = assignment.extract_location_and_nature(record)

    # Asserts
    assert location == "2900 CHAUTAUQUA AVE"
    assert nature == "911 Call Nature Unknown"


def test_create_db_success(mock_object, mock_sqlite):
    """Test successful creation of database with provided name"""
    # Mocks
    mock_cursor = mock_object
    mock_connection = mock_object
    mock_connection.cursor.return_value = mock_cursor
    mock_sqlite.return_value = mock_connection

    # Initialize
    db_name = "test.db"
    query = (
        "CREATE TABLE incidents(incident_time TEXT, incident_number TEXT, incident_location TEXT, "
        "incident_nature TEXT, incident_ori TEXT)"
    )

    # Execute
    conn = assignment.create_db(db_name)

    # Asserts
    mock_sqlite.assert_called_once_with(f'resources/{db_name}')
    mock_cursor.execute.assert_called_with(query)
    assert conn == mock_connection


def test_create_db_failure(mock_object, mock_sqlite):
    """Test exception in creation of database with provided name"""
    # Mocks
    mock_connection = mock_object
    mock_connection.cursor.return_value = Exception("Test exception")
    mock_sqlite.return_value = mock_connection

    # Execute
    db_name = "test.db"
    result = assignment.create_db(db_name)

    #  Asserts
    mock_sqlite.assert_called_once_with(f'resources/{db_name}')
    assert result is None


def test_populate_db_success(mock_object):
    """Test if database is being populated successfully"""
    # Mock
    mock_db = mock_object

    # Initialize
    sample_incidents = [
        {
            "incident_time": "16:07",
            "incident_number": "2024-00000153",
            "incident_location": "1000 108TH AVE SE",
            "incident_nature": "Reckless Driving",
            "incident_ori": "OK0140200",
        }
    ]

    # Execute
    assignment.populate_db(mock_db, sample_incidents)

    # Asserts
    mock_db.execute.assert_called_once_with(
        "INSERT INTO incidents (incident_time, incident_number, incident_location, incident_nature, "
        "incident_ori) VALUES (?, ?, ?, ?, ?)",
        (
            "16:07",
            "2024-00000153",
            "1000 108TH AVE SE",
            "Reckless Driving",
            "OK0140200",
        ),
    )
    mock_db.commit.assert_called_once()


def test_populate_db_failure(mock_object):
    """Test exception in populating database"""
    # Mocks
    mock_db = mock_object
    mock_db.execute.side_effect = Exception("Test exception")

    # Initialize
    sample_incidents = [
        {
            "incident_time": "16:07",
            "incident_number": "2024-00000153",
            "incident_location": "1000 108TH AVE SE",
            "incident_nature": "Reckless Driving",
            "incident_ori": "OK0140200",
        }
    ]

    # Execute
    assignment.populate_db(mock_db, sample_incidents)

    # Asserts
    mock_db.execute.assert_called_once_with(
        "INSERT INTO incidents (incident_time, incident_number, incident_location, incident_nature, "
        "incident_ori) VALUES (?, ?, ?, ?, ?)",
        (
            "16:07",
            "2024-00000153",
            "1000 108TH AVE SE",
            "Reckless Driving",
            "OK0140200",
        ),
    )
    mock_db.commit.assert_not_called()


def test_status_success(mock_object):
    """Test status for successful in fetching data from database"""
    # Mocks
    mock_cursor = mock_object
    mock_connection = mock_object
    mock_records = [("911 Call Nature Unknown", 4), ("Abdominal Pains/Problems", 6)]
    mock_cursor.fetchall.return_value = mock_records
    mock_connection.cursor.return_value = mock_cursor

    # Initialize
    query = """
        SELECT incident_nature, COUNT(*) as count
        FROM incidents
        GROUP BY incident_nature
        ORDER BY count DESC, incident_nature ASC;
        """

    # Execute
    assignment.status(mock_connection)

    # Asserts
    mock_connection.cursor.assert_called_once()
    mock_cursor.execute.assert_called_with(query)
    mock_cursor.fetchall.assert_called_once()
    mock_connection.close.assert_called_once()


def test_status_failure(mock_object):
    """Test status for exception in fetching data from database"""
    # Mocks
    mock_cursor = mock_object
    mock_connection = mock_object
    mock_cursor.execute.side_effect = Exception("Test exception")
    mock_connection.cursor.return_value = mock_cursor

    # Initialize
    query = """
        SELECT incident_nature, COUNT(*) as count
        FROM incidents
        GROUP BY incident_nature
        ORDER BY count DESC, incident_nature ASC;
        """

    # Execute
    assignment.status(mock_connection)

    # Asserts
    mock_connection.cursor.assert_called_once()
    mock_cursor.execute.assert_called_with(query)
    mock_cursor.fetchall.assert_not_called()
    mock_connection.close.assert_called_once()
