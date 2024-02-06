# CIS6930SP24 -- Project0

#### Name: Pratiksha Deodhar

## Project description
Norman, Oklahoma police department regularly reports incidents, arrests, and other activities. Our goal in this project
is to extract incident data from their database API and load it into database so that count of each occurance of nature can be captured and 
printed. 

## How to install
### Download pyenv, install python 3.11 and set it globally
- curl https://pyenv.run | bash
- pyenv install 3.11
- pyenv global 3.11

### Install required libraries
- pipenv install pypdf 
- pipenv install sqlite3
- pipenv install pytest
- pipenv install pytest-mock

## How to run
pipenv run python assignment0/main.py --incidents &lt;url&gt;

![video](video)


## Functions

### main
This function serves as the central entry point for the script designed to fetch, process, and store incident data from a provided URL into a SQLite database.
The function does not return a value. Its primary role is to execute a series of operations as well as potentially display summaries of the stored data.
It uses argparse to parse command-line arguments, requiring a URL to the incident summary as an input (--incidents), which it then passed to the main function.
- Function arguments: url
- Return Value : None

### delete_existing_db
This function deletes the database if it exists so that user need not require to manually delete the database every time
the code is run. 
- Function arguments: db_name
- Return value: None

### fetch_incidents
This function takes a URL as string and uses the `urllib.request` library to grab one incident pdf for the Norman Police Report Webpage.
- Function arguments: url
- Return value: incident data from url in binary format

### extract_incidents
This function is designed to process binary data of a PDF document, extract text content from each page, and then 
compile the text into a structured format, presumably a list of incidents.
- Function arguments: incident data from `fetch_incidents` function
- Return value: list of incidents

### extract_page_text
This function is designed to extract text in the form of list of strings where each string represents a line of text 
extracted from the current page, with special considerations for the first and last pages of the document.
- Function arguments: page, page_num, tot_pages
- Return value: split_incidents, which is a list of strings

### split_all_incidents
This function is designed to process a block of text (page_text) and extract individual incidents from it
- Function arguments: page_text, entire page content
- Return value: list of incidents of particular page

### refactor_page_data
This function processes a list of strings, each representing a line of text extracted from a PDF page, and transforms
this text to get data of incident's time, number, location, nature, ORI.
- Function arguments: page_text, which is a list of strings
- Return value: page_incidents, which is a list of dictionary with all incident arguments

### extract_location_and_nature
This function is designed to parse a segment of text and separate it into two components: the location and the nature 
of an incident. This parsing is based on certain conditions related to the content and its format.
- Function arguments: record, which is a segment of individual record list
- Return value: loc_str, nature_str

### create_db
This function is designed to create a new SQLite database and create a table within it for storing incident data.
- Function arguments: db_name
- Return value: database connection object

### populate_db
This function is designed to insert a collection of incident records into incidents table in the created database
- Function arguments: database connection object
- Return value: None

### status
This function is designed to query an SQLite database to group incident records by their nature, count the number of 
occurrences of each distinct nature, and then print out the records in order by count DESC and nature ASC.
- Function arguments: database connection object
- Return value: None

## Database Development
Execution of code checks if the database exists. If it exists, it first removes the database and then create a new
database "norman_pd.db" within resources directory. It also creates a table "incidents" within
the database which has the following columns - Incident Time, Incident Number, Location, Nature, Incident ORI.
Incidents are collected and then populated into the database in one go. 

## Bugs and Assumptions
- There will be only 5 columns in the pdf and order of columns will be preserved. After splitting list, index 1 will give time, index 2 will give incident number, last index will give incident ori, rest index will be used to extract location and nature
- Page 0 of pdf will have a header and last page will have a footer which needs to be removed
- Location includes - float, decimal, uppercase and special characters( "/", ";"). "MVA", "COP", "EMS", "911", "RAMPMVA", "HWYMotorist", "RAMPMotorist" are exceptions to this logic hence they are handled in each unique way
- Anything not included in location will be included in nature. Once we start writing into nature, nothing will be appended to location as location preceds nature column