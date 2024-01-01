import argparse
import re
import ujson
import ipaddress

# Each "wk*-" hostname is associated with a location and this mapping was manually built utilizing their documentation
# See https://docs.hetrixtools.com/uptime-monitoring-ip-addresses/ and https://hetrixtools.com/resources/uptime-monitor-ips.txt
wk_mapping = {
    'wk1': {
        'country_code': 'US',
        'city': 'New York',
        'subdivision_1_iso_code': 'US-NY'
    },
    'wk2': {
        'country_code': 'US',
        'city': 'San Francisco',
        'subdivision_1_iso_code': 'US-CA'
    },
    'wk3': {
        'country_code': 'NL',
        'city': 'Amsterdam',
        'subdivision_1_iso_code': 'NL-NH'
    },
    'wk4': {
        'country_code': 'GB',
        'city': 'London',
        'subdivision_1_iso_code': 'GB-LND'
    },
    'wk5': {
        'country_code': 'DE',
        'city': 'Frankfurt',
        'subdivision_1_iso_code': 'DE-HE'
    },
    'wk6': {
        'country_code': 'SG',
        'city': 'Singapore',
        'subdivision_1_iso_code': 'SG-01'
    },
    'wk7': {
        'country_code': 'US',
        'city': 'Dallas',
        'subdivision_1_iso_code': 'US-TX'
    },
    'wk8': {
        'country_code': 'AUS',
        'city': 'Sydney',
        'subdivision_1_iso_code': 'AU-NSW'
        },
    'wk9': {
        'country_code': 'BR',
        'city': 'São Paulo',
        'subdivision_1_iso_code': 'BR-SP'
    },
    'wk10': {
        'country_code': 'JP',
        'city': 'Tokyo',
        'subdivision_1_iso_code': 'JP-13'
    },
    'wk11': {
        'country_code': 'IN',
        'city': 'Mumbai',
        'subdivision_1_iso_code': 'IN-MH'
    },
    'wk12': {
        'country_code': 'PL',
        'city': 'Warsaw',
        'subdivision_1_iso_code': 'PL-MZ'
    }
}

def get_range(address):
    ip_address = ipaddress.ip_address(address)
    return str(ipaddress.ip_network(f"{ip_address}/{ip_address.max_prefixlen}", strict=False))

def extract_wk(hostname):
    match = re.match(r'^([a-zA-Z]+[0-9]+).*$', hostname)
    if match:
        return match.group(1)
    else:
        return None

def parse(file_path, json_file):
    data_list = []
    
    try:
        # Load existing data from the JSON file
        with open(json_file, 'r') as existing_file:
            data_list = ujson.load(existing_file)
    except FileNotFoundError:
        pass  # File doesn't exist yet, ignore and proceed with an empty list

    with open(file_path, 'r') as file:
        for line in file:
            match = re.match(r'^(\S+)\s+(\S+)', line)
            if match:
                hostname = match.group(1)
                ip_address = match.group(2)
                wk = extract_wk(hostname)

                if hostname and ip_address and wk:
                    if wk in wk_mapping:
                        if get_range(ip_address) not in data_list:
                            data_list[get_range(ip_address)] = wk_mapping[wk]
                        else:
                            print(f'(Hetrix) {get_range(ip_address)} is already in the dataset')
                    else:
                        print(f'(Hetrix) {wk} is not yet mapped')

        # Write the updated data back to the JSON file
        with open(json_file, 'w', encoding='utf-8') as json_file:
            ujson.dump(data_list, json_file, indent=0, ensure_ascii=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', help='path to the file')
    parser.add_argument('json_file', help='path to output JSON file')
    args = parser.parse_args()

    parse(args.file_path, args.json_file)
