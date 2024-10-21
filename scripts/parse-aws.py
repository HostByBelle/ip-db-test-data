## Kept for historical reference. AWS Now has a self-published geofeed which was added to their docs sometime between September 2nd and September 9th, 2024.
import argparse
import json

# Manually gathered from https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html
region_info = {
    "us-east-1": {
        "country_code": "US",
        "subdivision_1_iso_code": "US-VA",
    },
    "us-east-2": {
        "country_code": "US",
        "subdivision_1_iso_code": "US-OH"
    },
    "us-west-1": {
        "country_code": "US",
        "subdivision_1_iso_code": "US-CA"
    },
    "us-west-2": {
        "country_code": "US",
        "subdivision_1_iso_code": "US-OR"
    },
    "af-south-1": {
        "country_code": "ZA",
        "subdivision_1_iso_code": "US-OR"
    },
    "ap-east-1": {
        "country_code": "HK",
    },
    "ap-south-2": {
        "country_code": "IN",
    },
    "ap-southeast-3": {
        "country_code": "ID",
    },
    "ap-southeast-4": {
        "country_code": "AU",
    },
    "ap-south-1": {
        "country_code": "IN",
    },
    "ap-northeast-3": {
        "country_code": "JP",
    },
    "ap-northeast-2": {
        "country_code": "KR",
    },
    "ap-southeast-1": {
        "country_code": "SG",
    },
    "ap-southeast-2": {
        "country_code": "AU",
    },
    "ap-northeast-1": {
        "country_code": "JP",
    },
    "ca-central-1": {
        "country_code": "CA",
    },
    "eu-central-1": {
        "country_code": "DE",
    },
    "eu-west-1": {
        "country_code": "IE",
    },
    "eu-west-2": {
        "country_code": "GB",
    },
    "eu-south-1": {
        "country_code": "IT",
    },
    "eu-west-3": {
        "country_code": "FR",
    },
    "eu-south-2": {
        "country_code": "ES",
    },
    "eu-north-1": {
        "country_code": "SE",
    },
    "eu-central-2": {
        "country_code": "CH",
    },
    "il-central-1": {
        "country_code": "IL",
    },
    "me-south-1": {
        "country_code": "BH",
    },
    "me-central-1": {
        "country_code": "AE",
    },
    "sa-east-1": {
        "country_code": "BR",
    },
    "us-gov-east-1": {
        "country_code": "US",
    },
    "us-gov-west-1": {
        "country_code": "US",
    },
    "ca-west-1": {
        "country_code": "CA",
    },
    "cn-northwest-1": {
        "country_code": "CN",
    },
    "cn-north-1": {
        "country_code": "CN",
    },
    "ap-southeast-5": {
        "country_code": "MY",
    },
}


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


def parse(aws_ranges, json_file, ipver):
    data_list = {}

    try:
        # Load existing data from the JSON file
        with open(json_file, "r", encoding="utf-8") as existing_file:
            data_list = json.load(existing_file)
    except FileNotFoundError:
        pass  # File doesn't exist yet, ignore and proceed with an empty list

    with open(aws_ranges, "r", encoding="utf-8") as file:
        aws_ips = json.load(file)
        if ipver == "ipv6":
            prefixes = aws_ips["ipv6_prefixes"]
        else:
            prefixes = aws_ips["prefixes"]

        for prefix in prefixes:
            prefix_key = ipver + "_prefix"
            if prefix_key in prefix and prefix[prefix_key]:
                cidr = prefix[prefix_key]
                if prefix["region"] in region_info:
                    if cidr in data_list:
                        data_list[cidr] = merge(
                            data_list[cidr], region_info[prefix["region"]]
                        )
                    else:
                        data_list[cidr] = region_info[prefix["region"]]
                else:
                    if prefix["region"] != "GLOBAL":
                        region = prefix["region"]
                        print(f"(AWS) {region} is not yet mapped")

        # Write the updated data back to the JSON file
        with open(json_file, "w", encoding="utf-8") as json_file:
            json.dump(data_list, json_file, indent=0, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("aws_ranges", help="path to the AWS ranges JSON file")
    parser.add_argument("json_file", help="path to output JSON file")
    parser.add_argument("ipver", help="IP version (ip or ipv6)")
    args = parser.parse_args()

    parse(args.aws_ranges, args.json_file, args.ipver)
