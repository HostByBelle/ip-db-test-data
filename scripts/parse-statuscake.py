import argparse
import ujson
import ipaddress

def get_range(address):
    ip_address = ipaddress.ip_address(address)
    return str(ipaddress.ip_network(f"{ip_address}/{ip_address.max_prefixlen}", strict=False))

def parse(updown_data, json_file, ipver):
    data_list = []

    try:
        # Load existing data from the JSON file
        with open(json_file, 'r') as existing_file:
            data_list = ujson.load(existing_file)
    except FileNotFoundError:
        pass  # File doesn't exist yet, ignore and proceed with an empty list

    with open(updown_data, 'r') as file:
        statuscake_node = ujson.load(file)
        for node in statuscake_node:
            if not statuscake_node[node][ipver]:
                continue
            if get_range(statuscake_node[node][ipver]) not in data_list:
                data_list[get_range(statuscake_node[node][ipver])] = {
                    'country_code': statuscake_node[node]['countryiso']
                }
            else:
                print(f'(StatusCake) {get_range(statuscake_node[node][ipver])} is already in the dataset')

        # Write the updated data back to the JSON file
        with open(json_file, 'w', encoding='utf-8') as json_file:
            ujson.dump(data_list, json_file, indent=0, ensure_ascii=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('updown_data', help='path to the statuscake JSON file')
    parser.add_argument('json_file', help='path to output JSON file')
    parser.add_argument('ipver', help='IP version (ip or ipv6)')
    args = parser.parse_args()

    parse(args.updown_data, args.json_file, args.ipver)
