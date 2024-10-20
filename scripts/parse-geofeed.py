import csv
import json
import ipaddress
import argparse


def merge(existing, new):
    if existing == new:
        return existing
    else:
        keep = True
        # Loop through all of the existing values, if they match the new one we can merge them
        for key, value in existing.items():
            if new[key] != value:
                keep = False

        if keep:
            return existing + new
        else:
            print(f"Existing: {existing}. New: {new}")
            return existing


def parse(geofeed_csv, json_file, ipver):
    data_list = {}

    try:
        # Load existing data from the JSON file
        with open(json_file, "r", encoding="utf-8") as existing_file:
            data_list = json.load(existing_file)
    except FileNotFoundError:
        pass  # File doesn't exist yet, ignore and proceed with an empty list

    with open(geofeed_csv, "r") as file:
        csv_reader = csv.reader(file)

        for row in csv_reader:
            # Ensure we skip over any rows which are comments
            try:
                if row[0].startswith("#"):
                    continue
            except IndexError:
                continue
            
            # Generate a message for an incomplete row
            if len(row) < 4:
                print(f"Geofeed file: {geofeed_csv} has rows that are incomplete.")
                continue

            # Record the row
            network = ipaddress.ip_network(row[0], strict=False)
            if (ipver == "ip" and network.version == 4) or (
                ipver == "ipv6" and network.version == 6
            ):
                properties = {
                    "country_code": row[1],
                    "subdivision_1_iso_code": row[2],
                    "city": row[3],
                    "postal_code": row[4],
                }
                if row[0] in data_list:
                    data_list[row[0]] = merge(data_list[row[0]], properties)
                else:
                    data_list[row[0]] = properties

        # Write the updated data back to the JSON file
        with open(json_file, "w", encoding="utf-8") as json_file:
            json.dump(data_list, json_file, indent=0, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("geofeed_csv", help="path to the RFC 8805 Geofeed CSV file")
    parser.add_argument("json_file", help="path to output JSON file")
    parser.add_argument("ipver", help="IP version (ip or ipv6)")
    args = parser.parse_args()

    parse(args.geofeed_csv, args.json_file, args.ipver)
