import requests

def lookup_ip(ip):
    """Look up geolocation and network info for a single IP using ip-api.com."""
    url = f"http://ip-api.com/json/{ip}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
    except requests.RequestException as e:
        print(f"[!] Request failed: {e}")
        return

    # ip-api returns status "success" or "fail" — always check this first
    if data.get("status") != "success":
        print(f"[!] Lookup failed: {data.get('message', 'unknown error')}")
        return

    # Pull the fields we care about (.get avoids a crash if one is missing)
    print(f"\nResults for {data.get('query')}")
    print("-" * 40)
    print(f"Country : {data.get('country')}")
    print(f"Region  : {data.get('regionName')}")
    print(f"City    : {data.get('city')}")
    print(f"Coords  : {data.get('lat')}, {data.get('lon')}")
    print(f"ISP     : {data.get('isp')}")
    print(f"Org     : {data.get('org')}")
    print(f"ASN     : {data.get('as')}")
    print(f"Zip     : {data.get('zip')}")
    print(f"Timezone: {data.get('timezone')}")


if __name__ == "__main__":
    ip = input("Enter an IP address: ").strip()
    if ip:
        lookup_ip(ip)
    else:
        print("[!] No IP entered.")
