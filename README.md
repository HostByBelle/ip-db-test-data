# IP Database Testing Data

This repository automatically builds both IPv4 and IPv6 information to be used for testing IP address databases (geolocation primarily).

## Data sources utilized

- [Pingdom probe server data](https://www.pingdom.com/rss/probe_servers.xml)
  - IP address types: `IPv4`, `IPv6`
  - Data available: `Country code`, `Country name`, `City`, `Region`
- [Hetrix Monitoring IPs](https://docs.hetrixtools.com/uptime-monitoring-ip-addresses/)
  - IP address types: `IPv4`
  - Data available: `Country code`, `City`
- [Updown.io Monitoring IPs](https://updown.io/api/nodes)
  - IP address types: `IPv4`, `IPv6`
  - Data available: `Country code`, `City`, `Latitude`, `Longitude`
- [AWS IP Address Ranges](https://ip-ranges.amazonaws.com/ip-ranges.json)
  - IP address types: `IPv4`, `IPv6`
  - Data available: `Country code`
- [Oracle Cloud IP Address Ranges](https://docs.oracle.com/en-us/iaas/tools/public_ip_ranges.json)
  - IP address types: `IPv4`
  - Data available: `Country code`
