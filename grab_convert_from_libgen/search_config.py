def get_request_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://libgen.rs/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


def get_mirror_sources():
    # This is used by Metadata.get_metadata() method.
    mirror_sources = ["GET", "Cloudflare", "IPFS.io", "Infura", "Pinata"]
    return mirror_sources
