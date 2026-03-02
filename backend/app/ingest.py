import uuid
import tldextract
import os
import aiohttp

VT_API_KEY = os.getenv("VT_API_KEY", "")

def parse_email_event(payload: dict):
    """
    Normalize incoming payload and extract domains.
    Expected payload keys: subject, from, to (list), body, urls (list)
    """
    eid = str(uuid.uuid4())
    subject = payload.get("subject", "")
    sender = payload.get("from")
    to = payload.get("to", [])
    body = payload.get("body", "")
    urls = payload.get("urls", []) or []
    url_domain_map = {}
    domains = set()
    for u in urls:
        try:
            ext = tldextract.extract(u)
            domain = ".".join(part for part in (ext.domain, ext.suffix) if part)
            if domain:
                url_domain_map[u] = domain
                domains.add(domain)
        except Exception:
            continue

    # simple heuristic risk can be set by risk module (optional)
    return {
        "id": eid,
        "subject": subject,
        "from": sender,
        "to": to,
        "body": body,
        "urls": urls,
        "url_domain_map": url_domain_map,
        "domains": list(domains),
        "risk": 0.0
    }

async def enrich_domain_async(neo_handler, domain: str):
    """
    Optional: fetch VirusTotal domain info (if VT_API_KEY is set) and update domain node.
    """
    if not VT_API_KEY:
        return
    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {"x-apikey": VT_API_KEY}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
                    # store as string to avoid complex types
                    neo_handler.update_domain_info(domain, {"vt_last_analysis": str(stats)})
    except Exception:
        pass
