from flask import Flask, render_template, request, Response
import requests
import ipaddress
import os
import csv
import io

app = Flask(__name__)

# Read the AbuseIPDB key from the environment — never hardcode it
ABUSEIPDB_KEY = os.environ.get("ABUSEIPDB_KEY")


def is_valid_ip(ip):
    """Return True only for a valid IPv4 or IPv6 address."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def lookup_ip(ip):
    """Return a dict of geo/network info for an IP, or an error dict."""
    fields = ("status,message,query,country,regionName,city,zip,"
              "lat,lon,timezone,isp,org,as,proxy,hosting,mobile")
    url = f"http://ip-api.com/json/{ip}?fields={fields}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
    except requests.RequestException as e:
        return {"error": f"Request failed: {e}"}

    if data.get("status") != "success":
        return {"error": data.get("message", "Lookup failed")}

    return data


def check_reputation(ip):
    """Query AbuseIPDB for an IP's abuse score. Returns a dict or None."""
    if not ABUSEIPDB_KEY:
        return None

    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Key": ABUSEIPDB_KEY, "Accept": "application/json"}
    params = {"ipAddress": ip, "maxAgeInDays": 90}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        data = r.json().get("data", {})
    except requests.RequestException:
        return None

    return {
        "score": data.get("abuseConfidenceScore"),   # 0–100
        "reports": data.get("totalReports"),
        "last_reported": data.get("lastReportedAt"),
    }


def process_batch(raw_text):
    """Take pasted text, pull out valid IPs (one per line), look each up."""
    rows = []
    # Split on new lines and commas, strip blanks
    candidates = [x.strip() for x in raw_text.replace(",", "\n").splitlines()]
    candidates = [c for c in candidates if c]

    # Cap the batch so we don't hit API rate limits (ip-api = 45/min free)
    for ip in candidates[:40]:
        if not is_valid_ip(ip):
            rows.append({"query": ip, "error": "Invalid IP"})
            continue
        data = lookup_ip(ip)
        if "error" in data:
            rows.append({"query": ip, "error": data["error"]})
        else:
            rep = check_reputation(ip)
            data["abuse_score"] = rep["score"] if rep else ""
            rows.append(data)
    return rows


def make_csv(rows):
    """Turn the batch results into a downloadable CSV file."""
    output = io.StringIO()
    fieldnames = ["query", "country", "city", "isp", "as",
                  "proxy", "hosting", "abuse_score", "error"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=ip_intel_results.csv"},
    )


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        ip = request.form.get("ip", "").strip()
        if not ip:
            error = "Please enter an IP address."
        elif not is_valid_ip(ip):
            error = "That doesn't look like a valid IP address."
        else:
            data = lookup_ip(ip)
            if "error" in data:
                error = data["error"]
            else:
                result = data
                result["reputation"] = check_reputation(ip)

    return render_template("index.html", result=result, error=error)


@app.route("/batch", methods=["GET", "POST"])
def batch():
    rows = None
    if request.method == "POST":
        raw = request.form.get("ips", "")

        # If the "Download CSV" button was used, return a file instead of a page
        if request.form.get("action") == "csv":
            rows = process_batch(raw)
            return make_csv(rows)

        rows = process_batch(raw)

    return render_template("batch.html", rows=rows)


if __name__ == "__main__":
    # Localhost only, debug off — safe defaults
    app.run(host="127.0.0.1", port=5001, debug=False)
