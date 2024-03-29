import argparse
import json
import xml.etree.ElementTree as ET
import ipaddress

PINGDOM_NAMESPACE = "http://www.pingdom.com/ns/PingdomRSSNamespace"


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


def parse_xml(xml_file, ip_type, json_file):
    tree = ET.parse(xml_file, parser=ET.XMLParser(encoding="utf-8"))
    root = tree.getroot()

    data_list = {}

    try:
        # Load existing data from the JSON file
        with open(json_file, "r", encoding="utf-8") as existing_file:
            data_list = json.load(existing_file)
    except FileNotFoundError:
        pass  # File doesn't exist yet, ignore and proceed with an empty list

    for item in root.iterfind(".//item"):
        ip_address_element = item.find(
            f"pingdom:{ip_type}", {"pingdom": PINGDOM_NAMESPACE}
        )
        if ip_address_element is None:
            continue
        ip_address = ip_address_element.text

        if ip_address is None or ip_address == "NULL":
            continue

        country_element = item.find("pingdom:country", {"pingdom": PINGDOM_NAMESPACE})
        country_code = country_element.attrib.get("code", "")

        city = item.find("pingdom:city", {"pingdom": PINGDOM_NAMESPACE}).text

        cidr = get_range(ip_address)
        properties = {
            "country_code": country_code,
            "city": city,
        }
        if cidr in data_list:
            data_list[cidr] = merge(data_list[cidr], properties)
        else:
            data_list[cidr] = properties

    # Write the updated data back to the JSON file
    with open(json_file, "w", encoding="utf-8") as json_file:
        json.dump(data_list, json_file, indent=0, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("xml_file", help="path to XML file")
    parser.add_argument("json_file", help="path to output JSON file")
    parser.add_argument("ip_type", help="type of IP address")
    args = parser.parse_args()

    parse_xml(args.xml_file, args.ip_type, args.json_file)


if __name__ == "__main__":
    main()
