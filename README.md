# IP Database Testing Data

This repository automatically builds both IPv4 and IPv6 information to be used for testing IP address databases (geolocation primarily).

## Data sources utilized

- [Pingdom probe server data](https://www.pingdom.com/rss/probe_servers.xml)
  - IP address types: `IPv4`, `IPv6`
  - Data available: `Country Code`, `Country Name`, `City`, `Region`
- [Hetrix Monitoring IPs](https://docs.hetrixtools.com/uptime-monitoring-ip-addresses/)
  - IP address types: `IPv4`
  - Data available: `Country Code`, `City`
- [Updown.io Monitoring IPs](https://updown.io/api/nodes)
  - IP address types: `IPv4`, `IPv6`
  - Data available: `Country Code`, `City`, `Latitude`, `Longitude`
- [AWS IP Address Ranges](https://ip-ranges.amazonaws.com/ip-ranges.json)
  - IP address types: `IPv4`, `IPv6`
  - Data available: `Country Code`
- [Oracle Cloud IP Address Ranges](https://docs.oracle.com/en-us/iaas/tools/public_ip_ranges.json)
  - IP address types: `IPv4`
  - Data available: `Country Code`
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

### Data Processing

Each release will undergo a final "processing" step to ensure the generated data is of good quality.
The order of processing is as follows:

1. Basic de-duplication by removing duplicate entries of the same CIDR.
   - A warning will be generated if a duplicate does not contain the same data as it's original.
   - Only the first instance of a CIDR will be retained in the final data source.
2. The de-duplicated list is then sorted in decending order by the quantity of IP addresses in each CIDR
3. Any CIDRs which are private networks are discarded.
4. Any 3-letter country codes are converted to 2 letter country codes.
5. Next all CIDRs are looped through and compared against previous CIDRs to identify any overlaps / subnets.
   - A subnet is retained and any differing data from the parent (supernet) network is considered valid.
   - Any overlapping CIDRs are simply discarded with a message as of this moment.
6. The final dataset after processing is written to the JSON file before then being uploaded to the release.
