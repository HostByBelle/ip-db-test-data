import argparse
import ujson
import ipaddress
import pycountry
import time

# Some global stats
totalIPs = 0
duplicatedCIDRs = 0
overlappedCIDRs = 0
ignoredPrivateCIDRs = 0

def convert_to_2_letter_code(three_letter_code):
    try:
        country = pycountry.countries.get(alpha_3=three_letter_code)
        if country:
            return country.alpha_2
        else:
            return 'Not found'
    except Exception as e:
        print(f'Error: {e}')
        return None

# Quickly handle duplicate CIDR entries.
def deduplicate(ip_data_list):
    global duplicatedCIDRs
    ip_entries_dict = {}

    for entry in ip_data_list:
        ip_range = entry['ip_range']
        
        if ip_range in ip_entries_dict:
            ip_entries_dict[ip_range].append(entry)
        else:
            ip_entries_dict[ip_range] = [entry]

    result = []

    # Check and handle any duplicates
    for ip_range, entries in ip_entries_dict.items():
        if len(entries) > 1:
            duplicatedCIDRs += len(entries)
            for duplicate_entry in entries:
                # If there was a duplicate that didn't match the other entries for a given CIDR, print a message.
                if not (entries[0] == duplicate_entry):
                    print(f'{ip_range} has duplicates with mismatched info:')
                    print(f'{entries}')
            chosen_entry = entries[0]  # Only keep the first on
            result.append(chosen_entry)
        else:
            result.append(entries[0])

    return result

def process(json_file):
    global totalIPs, duplicatedCIDRs, overlappedCIDRs, ignoredPrivateCIDRs

    # Record the start time and memory usage before processing
    start_time = time.time()

    with open(json_file, 'r') as file:
        ip_data_list = ujson.load(file)

        # Quickly handle identical CIDR entries.
        ip_data_list = deduplicate(ip_data_list)

        # Sort the list based on the number of IP addresses in descending order
        ip_data_list.sort(key=lambda entry: ipaddress.ip_network(entry['ip_range'], strict=False).num_addresses, reverse=True)

        unique_ranges = set()
        result = []

        for entry in ip_data_list:
            # Make a copy of the entry, remove the IP range, and then check if it evaluates to false.
            # If it does, that IP range has no data associated with it and can be discarded
            entry_copy = entry.copy()
            del(entry_copy['ip_range'])
            if not entry_copy:
                continue

            ip_range = entry['ip_range']

            # Convert IP range to ipaddress object
            ip_network = ipaddress.ip_network(ip_range, strict=False)

            if ip_network.is_private:
                ignoredPrivateCIDRs += 1
                continue

            # Check IP ranges for overlaps
            if ip_network not in unique_ranges:
                if len(entry['country_code']) == 3:
                    entry['country_code'] = convert_to_2_letter_code(entry['country_code'])

                # Handle overlaps / subnets
                keep_network = True
                was_in_subnet = False
                
                for kept_entry in result:
                    existing_range = ipaddress.ip_network(kept_entry['ip_range'], strict=False)
                    if ip_network.subnet_of(existing_range):
                        test_data_2 = kept_entry.copy()
                        del(test_data_2['ip_range'])
                        # If a subnet has the same info as the supernet, remove it entirely.
                        if entry_copy == test_data_2:
                            keep_network = False
                        else:
                            # A subnet can have separate info from its larger network and as such should be handled as correct
                            keep_network = True
                            was_in_subnet = True
                    elif ip_network.overlaps(existing_range):
                        # Print a warning and discard the overlapping network
                        keep_network = False
                        overlappedCIDRs += 1
                        print(f'{ip_network} was discarded for overlapping with {existing_range}')

                if keep_network:
                    unique_ranges.add(ip_network)
                    result.append(entry)
                    if not was_in_subnet:
                        totalIPs += ip_network.num_addresses

        # Write the updated data back to the JSON file
        with open(json_file, 'w', encoding='utf-8') as json_file:
            ujson.dump(result, json_file, indent=0, ensure_ascii=False)

        # Calculate the time taken and memory used
        elapsed_time = time.time() - start_time

        print(f'{totalIPs:,} IPs in the final data source. There were {duplicatedCIDRs:,} duplicated, {overlappedCIDRs:,} overlapping, and {ignoredPrivateCIDRs:,} private CIDRs that were discarded.')
        print(f'Time taken: {elapsed_time:.2f} seconds')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('json_file', help='path to output JSON file')
    args = parser.parse_args()

    process(args.json_file)
