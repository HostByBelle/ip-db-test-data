import argparse
import json
import ipaddress


def get_range(address):
    ip_address = ipaddress.ip_address(address)
    return str(
        ipaddress.ip_network(f"{ip_address}/{ip_address.max_prefixlen}", strict=False)
    )


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


def parse(updown_data, json_file, ipver):
    data_list = {}

    try:
        # Load existing data from the JSON file
        with open(json_file, "r", encoding="utf-8") as existing_file:
            data_list = json.load(existing_file)
    except FileNotFoundError:
        pass  # File doesn't exist yet, ignore and proceed with an empty list

    with open(updown_data, "r") as file:
        statuscake_nodes = json.load(file)
        for node in statuscake_nodes:
            if not statuscake_nodes[node][ipver]:
                continue

            cidr = get_range(statuscake_nodes[node][ipver])
            properties = {"country_code": statuscake_nodes[node]["countryiso"]}
            if cidr in data_list:
                data_list[cidr] = merge(data_list[cidr], properties)
            else:
                data_list[cidr] = properties

        # Write the updated data back to the JSON file
        with open(json_file, "w", encoding="utf-8") as json_file:
            json.dump(data_list, json_file, indent=0, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("updown_data", help="path to the statuscake JSON file")
    parser.add_argument("json_file", help="path to output JSON file")
    parser.add_argument("ipver", help="IP version (ip or ipv6)")
    args = parser.parse_args()

    parse(args.updown_data, args.json_file, args.ipver)
