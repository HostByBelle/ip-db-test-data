import csv
import ujson
import ipaddress
import argparse

def parse(geofeed_csv, json_file, ipver):
    data_list = []

    try:
        # Load existing data from the JSON file
        with open(json_file, 'r') as existing_file:
            data_list = ujson.load(existing_file)
    except FileNotFoundError:
        pass  # File doesn't exist yet, ignore and proceed with an empty list

    with open(geofeed_csv, 'r') as file:
        csv_reader = csv.reader(file)
        
        for row in csv_reader:
            if not row[0].startswith('#'):
                network = ipaddress.ip_network(row[0], strict=False)
                if (ipver == 'ip' and network.version == 4) or (ipver == 'ipv6' and network.version == 6):
                    data_list.append({
                        'ip_range': row[0],
                        'country_code': row[1],
                        'subdivision_1_iso_code': row[2],
                        'city': row[3],
                        'postal_code': row[4],
                    })

        # Write the updated data back to the JSON file
        with open(json_file, 'w', encoding='utf-8') as json_file:
            ujson.dump(data_list, json_file, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('geofeed_csv', help='path to the RFC 8805 Geofeed CSV file')
    parser.add_argument('json_file', help='path to output JSON file')
    parser.add_argument('ipver', help='IP version (ip or ipv6)')
    args = parser.parse_args()

    parse(args.geofeed_csv, args.json_file, args.ipver)
