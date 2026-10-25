# IP Intelligence Lookup

A Flask web app that gathers geolocation, network ownership, and threat-reputation data for any IP address — the kind of enrichment a SOC analyst does when triaging a suspicious IP.

## Features

- **Geolocation:** country, region, city, coordinates (with a Google Maps link)
- **Network info:** ISP, organisation, ASN, timezone
- **Risk signals:** flags whether an IP is a known VPN/proxy, hosting/datacentre, or mobile network
- **Threat reputation:** pulls crowd-sourced abuse scores from AbuseIPDB (0–100) and total report count
- **Batch mode:** check up to 40 IPs at once and export results to CSV
- **Input validation:** every IP is validated as a real IPv4/IPv6 address before any request is made

## Why I built it

Investigators and SOC analysts constantly need to answer "where is this IP, who owns it, and is it malicious?" I built this to understand the IP-enrichment workflow end to end, using free public threat-intel APIs.

## Tech stack

- Python 3, Flask
- [ip-api.com](https://ip-api.com) for geolocation and network data
- [AbuseIPDB](https://www.abuseipdb.com) for threat reputation

## Security

- **Input validation:** IPs are checked with Python's `ipaddress` module before any lookup
- **No hardcoded secrets:** the AbuseIPDB key is read from an environment variable, never committed
- **XSS protection:** all output is auto-escaped by Jinja2 templates
- **Safe defaults:** binds to `127.0.0.1` only, with debug mode off

## Installation

```bash
git clone https://github.com/wadvaravish-afk/ip-intel.git
cd ip-intel
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Optional: enable threat reputation
export ABUSEIPDB_KEY="your-key-here"

python3 app.py
```

Then open http://127.0.0.1:5001.

## Limitations

- ip-api.com's free tier is limited to 45 requests/minute, so batch mode is capped at 40 IPs.
- AbuseIPDB's free tier allows 1,000 checks/day.
- A geolocation is an estimate of the IP's network location, not the precise location of a person.

## Ethics

For authorised and educational use only. This tool looks up IP addresses you have a legitimate reason to investigate (e.g. from your own logs). It does not track or de-anonymise individuals.
