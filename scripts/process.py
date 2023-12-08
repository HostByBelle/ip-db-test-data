import argparse
import json
import ipaddress
import pycountry

def convert_to_2_letter_code(three_letter_code):
    try:
        country = pycountry.countries.get(alpha_3=three_letter_code)
        if country:
            return country.alpha_2
        else:
            return "Not found"
    except Exception as e:
        print(f"Error: {e}")
        return None

# Quickly handle duplicate CIDR entries.
def deduplicate(ip_data_list):
    ip_entries_dict = {}

    for entry in ip_data_list:
        ip_range = entry["ip_range"]
        
        if ip_range in ip_entries_dict:
            ip_entries_dict[ip_range].append(entry)
        else:
            ip_entries_dict[ip_range] = [entry]

    result = []

    # Check and handle any duplicates
    for ip_range, entries in ip_entries_dict.items():
        if len(entries) > 1:
            for duplicate_entry in entries:
                # If there was a duplicate that didn't match the other entries for a given CIDR, print a message.
                if not (entries[0] == duplicate_entry):
                    print(f"{ip_range} has duplicates with mismatched info:")
                    print(f"{entries}")
            chosen_entry = entries[0]  # Only keep the first on
            result.append(chosen_entry)
        else:
            result.append(entries[0])

    return result

def process(json_file):

    with open(json_file, 'r') as file:
        ip_data_list = json.load(file)

        # Quickly handle identical CIDR entries.
        ip_data_list = deduplicate(ip_data_list)

        # Sort the list based on the IP range
        ip_data_list.sort(key=lambda entry: ipaddress.ip_network(entry["ip_range"], strict=False))

        unique_ranges = set()
        result = []

        for entry in ip_data_list:
            ip_range = entry["ip_range"]
            
            # Convert IP range to ipaddress object
            ip_network = ipaddress.ip_network(ip_range, strict=False)

            # Check IP ranges for overlaps
            if ip_network not in unique_ranges:
                if len(entry["country_code"]) == 3:
                    entry["country_code"] = convert_to_2_letter_code(entry["country_code"])

                # Handle overlaps / subnets
                keep_network = True
                for existing_range in unique_ranges:
                    if ip_network.subnet_of(existing_range):
                        # A subnet can have seperate info from it's larger network and as such shoyuld be handled as correct
                        keep_network = True
                    elif ip_network.overlaps(existing_range):
                        # Print a warning and discard the overlaping network
                        keep_network = False
                        print(f"{ip_network} was discarded for overlapping with {existing_range}")
                
                if keep_network:
                    unique_ranges.add(ip_network)
                    result.append(entry)

        # Write the updated data back to the JSON file
        with open(json_file, 'w', encoding='utf-8') as json_file:
            json.dump(result, json_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help="path to output JSON file")
    args = parser.parse_args()

    process(args.json_file)
