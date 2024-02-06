import argparse
from assignment0 import assignment


def main(url):
    # define database name
    db_name = "normanpd.db"

    # delete existing DB
    assignment.delete_existing_db(db_name)

    # get incident PDF data
    incident_data = assignment.fetch_incidents(url)

    # extract incident data
    incidents = assignment.extract_incidents(incident_data)

    # create new database
    db = assignment.create_db(db_name)

    # populate database table with extracted incidents
    assignment.populate_db(db, incidents)

    # print incident nature with their count
    assignment.status(db)


if __name__ == "__main__":
    # initialize command-line argument parsing
    parser = argparse.ArgumentParser()
    # define the required command-line argument '--incidents' for the incident summary URL
    parser.add_argument(
        "--incidents", type=str, required=True, help="Incident summary url."
    )
    # parse command-line arguments
    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)
