import argparse
import assignment0


def main(url):
    db_name = "norman_pd.db"

    # Delete existing DB
    assignment0.delete_existing_db(db_name)

    # Get incident PDF data
    incident_data = assignment0.fetch_incidents(url)

    # Extract incident data
    incidents = assignment0.extract_incidents(incident_data)

    # Create new database
    db = assignment0.create_db(db_name)

    assignment0.populate_db(db, incidents)

    # assignment0.print_record(db_name)

    assignment0.status(db)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--incidents", type=str, required=True, help="Incident summary url."
    )

    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)
