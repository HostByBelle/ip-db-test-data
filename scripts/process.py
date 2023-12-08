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

def process(json_file):

    with open(json_file, 'r') as file:
        unique_ranges = set()
        result = []
        list = json.load(file)
        for entry in list:
            ip_range = entry["ip_range"]
            
            # Check if IP range is not a duplicate
            if ip_range not in unique_ranges:
                if len(entry["country_code"]) == 3:
                    entry["country_code"] = convert_to_2_letter_code(entry["country_code"])

                unique_ranges.add(ip_range)
                result.append(entry)

        # Write the updated data back to the JSON file
        with open(json_file, 'w', encoding='utf-8') as json_file:
            json.dump(result, json_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help="path to output JSON file")
    args = parser.parse_args()

    process(args.json_file)
