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
        # Get current working directory path
        base_path = os.getcwd()
        # Build DB file path
        file_path = f"{base_path}/resources/{db_name}"
        # Delete DB file if exists
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
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 "
                          "Safari/537.17"
        }
        data = urllib.request.urlopen(
            urllib.request.Request(url, headers=headers)
        ).read()
        return data
    except Exception as ex:
        print("ERROR in fetching incidents: ", ex)


def extract_incidents(incident_data):
    """Extracts and gather incidents from PDF Document page-wise

    Params:
        incident_data (bytes): PDF document data
    Return:
        incidents (list[dict]): All incidents with extracted fields
    """
    # Convert download data to bites object
    pdf_buffer = io.BytesIO(incident_data)
    # Create PDFReader object
    reader = PdfReader(pdf_buffer)
    # Get total number of pages
    tot_pages = len(reader.pages)

    incidents = []
    for page_num in range(tot_pages):
        # Create specific page object
        page = reader.pages[page_num]
        # Extract text
        page_text = extract_page_text(page, page_num, tot_pages)
        hh = refactor_page_data(page_text)
        incidents.extend(hh)

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
        page_text = page.extract_text()[57:-55]
        split_incidents = split_all_incidents(page_text)
    elif page_num == tot_pages - 1:
        page_text = page.extract_text()
        split_incidents = split_all_incidents(page_text, 'last')
    else:
        page_text = page.extract_text()
        split_incidents = split_all_incidents(page_text)

    return split_incidents


def split_all_incidents(page_text, page_type=None):
    """Splits each incident based on date and time.

    Params:
    - page_text (str): page content
    - page_type (str/None): type of page, could be 'last' or 'None'
    Return:
         extracted_incident (list): Extract incidents
    """
    pattern = r'(?=\d{1,2}/\d{1,2}/\d{4})'
    extracted_incidents = re.split(pattern, page_text.strip())
    if page_type == 'last':
        extracted_incidents = extracted_incidents[:-1]
    extracted_incidents = [incident for incident in extracted_incidents if incident]

    return extracted_incidents


def refactor_page_data(page_text):
    """Filter specific fields from the page content.

    Params:
        page_text (list): extracted incidents
    Return:
        page_incidents (List[dict]): List of extracted fields of each incident
    """
    page_incidents = []
    for i in range(len(page_text)):
        record = page_text[i].split()
        rec_time = record[1]
        rec_incident_num = record[2]
        rec_incident_ori = record[-1]

        location, nature = extract_location_and_nature(record[3: len(record) - 1])

        if len(rec_incident_num) > 13:
            location = rec_incident_num[13:] + ' ' + location
            rec_incident_num = rec_incident_num[:13]

        page_incidents.append(
            {
                "incident_time": rec_time,
                "incident_number": rec_incident_num,
                "incident_location": location,
                "incident_nature": nature,
                "incident_ori": rec_incident_ori,
            }
        )

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
        if len(nature) == 0 and rec != "MVA" and rec != "COP" and rec != "EMS" and (rec.isdecimal() or rec.isupper() or
                                                                                    rec == "/" or ';' in rec):
            location.append(rec)
        elif rec == 'HWYMotorist':
            location.append('HWY')
            nature.append('Motorist')
        else:
            nature.append(rec)

    try:
        if location[-1].isnumeric() and len(location[-1]) > 1:
            nature.insert(0, location[-1])
            location.pop()
    except Exception as ex:
        print("ERROR in Location: ", ex)
    loc_str = " ".join(location)
    nature_str = " ".join(nature)

    return loc_str, nature_str


def create_json(incidents):
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
        db_file_loc = f'../cis6930sp24-assignment0/resources/{db_name}'
        conn = sqlite3.connect(db_file_loc)
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE incidents(incident_time TEXT, incident_number TEXT, incident_location TEXT, incident_nature "
            "TEXT, incident_ori TEXT)"
        )
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

        # Query to get distinct incident_nature and their count
        cur.execute(
            """
        SELECT incident_nature, COUNT(*) as count 
        FROM incidents 
        GROUP BY incident_nature
        ORDER BY count DESC, incident_nature ASC
        """
        )

        # Fetch all rows from the result set
        rows = cur.fetchall()

        for row in rows:
            print(f"{row[0]}|{row[1]}")
    except Exception as ex:
        print("ERROR in fetching Status: ", ex)
    finally:
        conn.close()


def print_record(db_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)

    # Create a cursor object using the cursor() method
    cursor = conn.cursor()

    # SQL query to retrieve data
    query = "SELECT * FROM incidents"

    try:
        # Execute the SQL command
        cursor.execute(query)

        # Fetch all the rows
        records = cursor.fetchall()

        # Print the records
        for row in records:
            print(row)  # Each row is a tuple representing a record

    except sqlite3.Error as e:
        print("Database error:", e)

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()
