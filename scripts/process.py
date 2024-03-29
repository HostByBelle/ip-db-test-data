import argparse
import json
import ipaddress
import pycountry
import time

# Some global stats
totalIPs = 0
overlappedCIDRs = 0
ignoredPrivateCIDRs = 0


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


def process(json_file):
    global totalIPs, overlappedCIDRs, ignoredPrivateCIDRs

    # Record the start time and memory usage before processing
    start_time = time.time()

    with open(json_file, "r", encoding="utf-8") as file:
        ip_data_list = json.load(file)
        result = {}

        ip_data_list = dict(
            sorted(
                ip_data_list.items(),
                key=lambda item: ipaddress.ip_network(item[0]).num_addresses,
                reverse=True,
            )
        )

        for cidr, entry in ip_data_list.items():
            if not entry:
                continue

            # Convert IP range to ipaddress object
            ip_network = ipaddress.ip_network(cidr, strict=False)

            if ip_network.is_private:
                ignoredPrivateCIDRs += 1
                continue

            # Check IP ranges for overlaps
            if len(entry["country_code"]) == 3:
                entry["country_code"] = convert_to_2_letter_code(entry["country_code"])

            # Handle overlaps / subnets
            keep_network = True
            was_in_subnet = False

            for kept_cidr, kept_entry in result.items():
                existing_range = ipaddress.ip_network(kept_cidr, strict=False)
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
                    print(
                        f"{ip_network} was discarded for overlapping with {existing_range}"
                    )

            if keep_network:
                result[cidr] = entry
                if not was_in_subnet:
                    totalIPs += ip_network.num_addresses

        # Write the updated data back to the JSON file
        with open(json_file, "w", encoding="utf-8") as json_file:
            json.dump(result, json_file, indent=0, ensure_ascii=False)

        # Calculate the time taken and memory used
        elapsed_time = time.time() - start_time

        print(f"{totalIPs:,} IPs in the final data source.")
        print(
            f"There were {overlappedCIDRs:,} overlapping and {ignoredPrivateCIDRs:,} private CIDRs that were discarded."
        )
        print(f"Time taken: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help="path to output JSON file")
    args = parser.parse_args()

    process(args.json_file)
