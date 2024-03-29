# IP Database Testing Data

This repository automatically builds both IPv4 and IPv6 information to be used for testing IP address databases. Due to the nature of how this data is collected, it may also be valuable as supplemental data when building a database and can be considered known-good data.

## Data sources utilized

The data is built utilizing self-published data by various providers. No 3rd party data is utilized and is considered inherently unreliable for the purposes of this data.

- [Pingdom probe server data](https://www.pingdom.com/rss/probe_servers.xml)
  - IP address types: `IPv4`, `IPv6`
  - Data available: `Country Code`, `Country Name`, `City`
- [Hetrix Monitoring IPs](https://hetrixtools.com/resources/uptime-monitor-ips.txt)
  - IP address types: `IPv4`
  - Data available: `Country Code`, `City`, `Subdivision Code`
  - Note: Utilizes a [hand-built mapping](https://github.com/HostByBelle/ip-db-test-data/blob/main/scripts/parse-hetrix.py#L6) between Hetrix's hostnames and their locations.
- [Updown.io Monitoring IPs](https://updown.io/api/nodes)
  - IP address types: `IPv4`, `IPv6`
  - Data available: `Country Code`, `City`, `Latitude`, `Longitude`
- [AWS IP Address Ranges](https://ip-ranges.amazonaws.com/ip-ranges.json)
  - IP address types: `IPv4`, `IPv6`
  - Data available: `Country Code`
  - Note: Utilizes a [hand-built mapping](https://github.com/HostByBelle/ip-db-test-data/blob/main/scripts/parse-aws.py#L6) between AWS's region IDs and their locations.
- [Oracle Cloud IP Address Ranges](https://docs.oracle.com/en-us/iaas/tools/public_ip_ranges.json)
  - IP address types: `IPv4`
  - Data available: `Country Code`
  - Note: Utilizes a [hand-built mapping](https://github.com/HostByBelle/ip-db-test-data/blob/main/scripts/parse-oracle.py#L5) between Oracle's region IDs and their locations.
- [Linode Geofeed](https://geoip.linode.com/)
  - IP address types: `IPv4`, `IPv6`
  - Data available: `Country Code`, `Subdivision Code`, `City Name`, `Postal Code`
- [DigitalOcean Geofeed](https://digitalocean.com/geo/google.csv)
  - IP address types: `IPv4`, `IPv6`
  - Data available: `Country Code`, `Subdivision Code`, `City Name`, `Postal Code`
- [Vultr Geofeed](https://digitalocean.com/geo/google.csv)
  - IP address types: `IPv4`, `IPv6`
  - Data available: `Country Code`, `Subdivision Code`, `City Name`, `Postal Code`
- [Starlink Geofeed](https://geoip.starlinkisp.net/feed.csv)
  - IP address types: `IPv4`, `IPv6`
  - Data available: `Country Code`, `Subdivision Code`, `City Name`
- [Google Cloud Geofeed](https://www.gstatic.com/ipranges/cloud_geofeed)
  - IP address types: `IPv4`, `IPv6`
  - Data available: `Country Code`, `Subdivision Code`, `City Name`

## Data Processing

Each release will go through a few "processing" steps to ensure the generated data is of good quality.  
The order of processing is as follows:

1. During each parsing step, deduplication is performed. Identical CIDRs are merged if shared properties between the two match, if not the currently existing one will be retained.
2. The complete list is then sorted in decending order by the quantity of IP addresses in each CIDR
3. Any CIDRs which are private networks are discarded.
4. Any CIDRs which haven no data associated with them are discarded.
5. Any 3-letter country codes are converted to 2 letter country codes.
6. Next all CIDRs are looped through and compared against previous CIDRs to identify any overlaps / subnets.
   - A subnet is retained and any differing data from the parent (supernet) network is considered valid.
   - Any overlapping CIDRs are simply discarded with a message as of this moment.
   - If a subnet has identical information to it's supernet, it's removed from the dataset.
7. The final dataset after processing is written to the JSON file before then being uploaded to the release.

Unfortunately, this final step is proving to be quite slow due to it's time complexity which reduces the data size we can easily build.
If you have ideas on how to optimize this, please share!
