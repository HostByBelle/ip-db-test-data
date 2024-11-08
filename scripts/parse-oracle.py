import argparse
import json

# Manually gathered from https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm
region_info = {
    "ap-sydney-1": {
        "country_code": "AU",
    },
    "ap-melbourne-1": {
        "country_code": "AU",
    },
    "sa-saopaulo-1": {
        "country_code": "BR",
    },
    "sa-vinhedo-1": {
        "country_code": "BR",
    },
    "ca-montreal-1": {
        "country_code": "CA",
    },
    "ca-toronto-1": {
        "country_code": "CA",
    },
    "sa-santiago-1": {
        "country_code": "CL",
    },
    "sa-bogota-1": {
        "country_code": "CO",
    },
    "eu-paris-1": {
        "country_code": "FR",
    },
    "eu-marseille-1": {
        "country_code": "FR",
    },
    "eu-frankfurt-1": {
        "country_code": "DE",
    },
    "ap-hyderabad-1": {
        "country_code": "IN",
    },
    "ap-mumbai-1": {
        "country_code": "IN",
    },
    "il-jerusalem-1": {
        "country_code": "IL",
    },
    "eu-milan-1": {
        "country_code": "IT",
    },
    "ap-osaka-1": {
        "country_code": "JP",
    },
    "ap-tokyo-1": {
        "country_code": "JP",
    },
    "mx-queretaro-1": {
        "country_code": "MX",
    },
    "mx-monterrey-1": {
        "country_code": "MX",
    },
    "eu-amsterdam-1": {
        "country_code": "NL",
    },
    "me-jeddah-1": {
        "country_code": "SA",
    },
    "eu-jovanovac-1": {
        "country_code": "RS",
    },
    "ap-singapore-1": {
        "country_code": "SG",
    },
    "ap-singapore-2": {
        "country_code": "SG",
    },
    "af-johannesburg-1": {
        "country_code": "ZA",
    },
    "ap-seoul-1": {
        "country_code": "KR",
    },
    "ap-chuncheon-1": {
        "country_code": "KR",
    },
    "eu-madrid-1": {
        "country_code": "ES",
    },
    "eu-stockholm-1": {
        "country_code": "SE",
    },
    "eu-zurich-1": {
        "country_code": "CH",
    },
    "me-abudhabi-1": {
        "country_code": "AE",
    },
    "me-dubai-1": {
        "country_code": "AE",
    },
    "uk-london-1": {
        "country_code": "GB",
    },
    "uk-cardiff-1": {
        "country_code": "GB",
    },
    "us-ashburn-1": {
        "country_code": "US",
        "subdivision_1_iso_code":"US-VA"
    },
    "us-chicago-1": {
        "country_code": "US",
        "subdivision_1_iso_code":"US-IL"
    },
    "us-phoenix-1": {
        "country_code": "US",
        "subdivision_1_iso_code":"US-AZ"
    },
    "us-sanjose-1": {
        "country_code": "US",
        "subdivision_1_iso_code":"US-CA"
    },
    "sa-valparaiso-1": {
        "country_code": "CL",
    },
    "us-saltlake-2": { # Inferred from name - not listed on Oracle's docs
        "country_code": "US",
        "subdivision_1_iso_code":"US-UT"
    },
    "me-riyadh-1": {
        "country_code": "SA",
    }
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


def parse(updown_data, json_file):
    data_list = {}

    try:
        # Load existing data from the JSON file
        with open(json_file, "r", encoding="utf-8") as existing_file:
            data_list = json.load(existing_file)
    except FileNotFoundError:
        pass  # File doesn't exist yet, ignore and proceed with an empty list

    with open(updown_data, "r") as file:
        oracle_ips = json.load(file)
        for region in oracle_ips["regions"]:
            if region["region"] in region_info:
                for cidr in region["cidrs"]:
                    if cidr["cidr"] in data_list:
                        data_list[cidr["cidr"]] = merge(
                            data_list[cidr["cidr"]], region_info[region["region"]]
                        )
                    else:
                        data_list[cidr["cidr"]] = region_info[region["region"]]
            else:
                region = region["region"]
                print(f"(Oracle) {region} is not yet mapped")

        # Write the updated data back to the JSON file
        with open(json_file, "w", encoding="utf-8") as json_file:
            json.dump(data_list, json_file, indent=0, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("updown_data", help="path to the oracle cloud ranges JSON file")
    parser.add_argument("json_file", help="path to output JSON file")
    args = parser.parse_args()

    parse(args.updown_data, args.json_file)
