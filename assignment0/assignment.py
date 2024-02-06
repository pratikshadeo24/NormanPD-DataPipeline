import os
import io
import json
import re
import sqlite3
import urllib.request
from pypdf import PdfReader


def delete_existing_db(db_name):
    """Delete database file if it exists under resources.

    Params:
        db_name (str): name of database file
    Return:
        None
    Raise:
        Exception(if any) while deleting database file
    """
    try:
        # get current working directory path
        base_path = os.getcwd()
        # build DB file path
        file_path = f"{base_path}/resources/{db_name}"
        # delete DB file if exists
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as ex:
        print("ERROR in deleting database file: ", ex)


def fetch_incidents(url):
    """Download PDF data from provided URL

    Params:
        url (str): API to download PDF Document
    Return:
        data (bytes): Data of the PDF Document
    """
    try:
        # define a dictionary of HTTP headers to simulate a request from a web browser
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 "
                          "Safari/537.17"
        }
        # make an HTTP GET request to the specified URL with the headers
        data = urllib.request.urlopen(
            urllib.request.Request(url, headers=headers)
        ).read()
        # return the content of the HTTP response
        return data
    except Exception as ex:
        print("ERROR in fetching incidents: ", ex)


def extract_incidents(incident_data):
    """Extracts and gather incidents from PDF Document page-wise

    Params:
        incident_data (bytes): PDF document data
    Return:
        incidents (list): All incidents with extracted fields
    """
    # convert download data to bytes object
    pdf_buffer = io.BytesIO(incident_data)
    # create PDFReader object
    reader = PdfReader(pdf_buffer)
    # get total number of pages
    tot_pages = len(reader.pages)

    incidents = []
    for page_num in range(tot_pages):
        # create specific page object
        page = reader.pages[page_num]
        # extract text
        page_text = extract_page_text(page, page_num, tot_pages)
        # refactor page text to capture different fields of incident
        incidents.extend(refactor_page_data(page_text))

    create_json(incidents)
    return incidents


def extract_page_text(page, page_num, tot_pages):
    """Extract page text based on the page number.

    Params:
    - page (PageObject): specific page object
    - page_num (int): current page number
    - tot_pages (int): total number of pages in PDF document
    Return:
         split_incidents (List[str]): Extracted incidents
    """
    if page_num == 0:
        # extract the page text and remove header and column heading
        page_text = page.extract_text()[57:-55]
        # split the page text into individual incidents
        split_incidents = split_all_incidents(page_text)
    elif page_num == tot_pages - 1:
        # extract the page text
        page_text = page.extract_text()
        # split the page text into individual incidents
        split_incidents = split_all_incidents(page_text, 'last')
    else:
        # extract the page text
        page_text = page.extract_text()
        # split the page text into individual incidents
        split_incidents = split_all_incidents(page_text)

    # return incidents of a single page
    return split_incidents


def split_all_incidents(page_text, page_type=None):
    """Splits each incident based on date.

    Params:
    - page_text (str): page content
    - page_type (str/None): type of page, could be 'last' or 'None'
    Return:
         extracted_incident (list): Extract incidents
    """
    # regex for recognizing date
    pattern = r'(?=\d{1,2}/\d{1,2}/\d{4})'
    # split the page text into list of incidents using date regex
    extracted_incidents = re.split(pattern, page_text.strip())
    if page_type == 'last':
        # remove the footer from last page
        extracted_incidents = extracted_incidents[:-1]
    # filter out any empty strings
    extracted_incidents = [incident for incident in extracted_incidents if incident]

    # return extracted incidents
    return extracted_incidents


def refactor_page_data(page_text):
    """Filter specific fields from the page content.

    Params:
        page_text (list): extracted incidents
    Return:
        page_incidents (List): List of extracted fields of each incident
    """
    page_incidents = []
    for i in range(len(page_text)):
        # split individual incidents into tokens to extract fixed fields
        record = page_text[i].split()
        rec_time = record[1]
        rec_incident_num = record[2]
        rec_incident_ori = record[-1]

        if record[3: len(record)-1]:
            # extract location and nature
            location, nature = extract_location_and_nature(record[3: len(record)-1])
        else:
            location, nature = "", ""
        # handle edge case when extra text incident number has an extra text
        if len(rec_incident_num) > 13:
            location = rec_incident_num[13:] + ' ' + location
            rec_incident_num = rec_incident_num[:13]

        # collect each incident record
        page_incidents.append(
            {
                "incident_time": rec_time,
                "incident_number": rec_incident_num,
                "incident_location": location,
                "incident_nature": nature,
                "incident_ori": rec_incident_ori,
            }
        )

    # return extracted fields of all the incidents of a specific page
    return page_incidents


def extract_location_and_nature(record):
    """Extract location and nature of an incident.

    Params:
        record (list): segment of an incident
    Return:
    - loc_str (str): Location of an incident
    - nature_str (str): Nature of an incident
    Raise:
        Exception while modifying location and nature for an edge case
    """
    location, nature = [], []
    for rec in record:
        # handle location and nature edge cases
        if len(nature) == 0 and rec != "MVA" and rec != "COP" and rec != "EMS" and rec != "RAMPMVA" and (
                rec.isdecimal() or rec.isupper() or rec == "/" or ';' in rec or rec == '1/2'):
            location.append(rec)
        elif rec == 'HWYMotorist' or rec == 'RAMPMotorist':
            location.append(rec.split('Motorist')[0])
            nature.append('Motorist')
        elif rec == "RAMPMVA":
            location.append('RAMP')
            nature.append('MVA')
        else:
            nature.append(rec)

    try:
        if location:
            # handle edge case when location ends with numeric
            if location[-1].isnumeric() and len(location[-1]) != 1:
                nature.insert(0, location[-1])
                location.pop()
    except Exception as ex:
        print("ERROR in Location: ", ex)

    # convert location and nature into string
    loc_str = " ".join(location)
    nature_str = " ".join(nature)

    return loc_str, nature_str


def create_json(incidents):
    # create json out of extracted incidents
    with open("../incidents.json", "w") as f:
        json.dump(incidents, f, indent=4)


def create_db(db_name):
    """Creates database under resources dir.

    Params:
        db_name (str): name of the database
    Return:
        conn (sqlite3.Connection): Database connection object
    Raise:
        Exception while establishing connection / creating cursor / executing query
    """
    try:
        # define db path
        db_file_loc = f'resources/{db_name}'
        # establish db connection
        conn = sqlite3.connect(db_file_loc)
        # generate cursor object
        cur = conn.cursor()
        # create incident table
        cur.execute(
            "CREATE TABLE incidents(incident_time TEXT, incident_number TEXT, incident_location TEXT, incident_nature "
            "TEXT, incident_ori TEXT)"
        )
        # return DB connection object
        return conn
    except Exception as ex:
        print("ERROR in creating DB: ", ex)


def populate_db(db, incidents):
    """Populate database with all the extracted incidents.

    Params:
    - db (sqlite3.Connection): database connection object
    - incidents (list): list of all the extracted incidents
    Return:
        None
    Raise:
        Exception while data entry / missing key / saving database changes
    """
    try:
        # insert each incident record into table one by one
        for incident in incidents:
            db.execute(
                "INSERT INTO incidents (incident_time, incident_number, incident_location, incident_nature, "
                "incident_ori) VALUES (?, ?, ?, ?, ?)",
                (
                    incident["incident_time"],
                    incident["incident_number"],
                    incident["incident_location"],
                    incident["incident_nature"],
                    incident["incident_ori"],
                ),
            )
            # save inserted records
            db.commit()
    except Exception as ex:
        print("ERROR in populating DB: ", ex)


def status(conn):
    """Print distinct incident natures and their counts by grouping them.

    Params:
        conn (sqlite3.Connection): database connection object
    Return:
        None
    Raise:
        Exception while creating cursor / executing query / fetching records
    """
    try:
        cur = conn.cursor()

        # query to get distinct incident_nature and their count
        cur.execute(
            """
        SELECT incident_nature, COUNT(*) as count, 0 as sort_col
        FROM incidents
        WHERE incident_nature !=""
        GROUP BY incident_nature
        UNION ALL
        SELECT incident_nature, COUNT(*) as count, 1 as sort_col
        FROM incidents
        WHERE incident_nature =""
        ORDER BY sort_col ASC, count DESC, incident_nature ASC;
        """
        )

        # fetch all rows from the result set
        rows = cur.fetchall()

        for row in rows:
            # print the records
            if row[0] is not None:
                print(f"{row[0]}|{row[1]}")
    except Exception as ex:
        print("ERROR in fetching Status: ", ex)
    finally:
        conn.close()


def print_record(db_name):
    # connect to the SQLite database
    conn = sqlite3.connect(db_name)

    # create a cursor object using the cursor() method
    cursor = conn.cursor()

    # SQL query to retrieve data
    query = "SELECT * FROM incidents"

    try:
        # execute the SQL command
        cursor.execute(query)

        # fetch all the rows
        records = cursor.fetchall()

        # print the records
        for row in records:
            print(row)  # Each row is a tuple representing a record

    except sqlite3.Error as e:
        print("Database error:", e)

    finally:
        # close the cursor and connection
        cursor.close()
        conn.close()
