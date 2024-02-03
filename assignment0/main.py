import argparse
import assignment

def main(url):
    db_name = "norman_pd.db"

    # Delete existing DB
    assignment.delete_existing_db(db_name)

    # Get incident PDF data
    incident_data = assignment.fetch_incidents(url)

    # Extract incident data
    incidents = assignment.extract_incidents(incident_data)

    # Create new database
    db = assignment.create_db(db_name)

    assignment.populate_db(db, incidents)

    # assignment0.print_record(db_name)

    assignment.status(db)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--incidents", type=str, required=True, help="Incident summary url."
    )

    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)
