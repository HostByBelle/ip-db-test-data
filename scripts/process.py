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

def process(json_file):
    global totalIPs, duplicatedCIDRs, overlappedCIDRs, ignoredPrivateCIDRs

    # Record the start time and memory usage before processing
    start_time = time.time()

    with open(json_file, 'r') as file:
        ip_data_list = ujson.load(file)

        # Sort the list based on the number of IP addresses in descending order
        ip_data_list.sort(key=lambda ip_range: ipaddress.ip_network(ip_range, strict=False).num_addresses, reverse=True)

        unique_ranges = set()
        result = []

        for ip_range, entry in ip_data_list:
            # Make a copy of the entry, remove the IP range, and then check if it evaluates to false.
            # If it does, that IP range has no data associated with it and can be discarded
            if not entry:
                continue

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
                
                for kept_ip_range, kept_entry in result:
                    existing_range = ipaddress.ip_network(kept_ip_range, strict=False)
                    if ip_network.subnet_of(existing_range):
                        # If a subnet has the same info as the supernet, remove it entirely.
                        if entry == kept_entry:
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
