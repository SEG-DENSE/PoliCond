#!/usr/bin/env python3
"""Download a web page and export the accessibility tree for parsing."""

# origin repo: https://github.com/UCI-Networking-Group/PoliGraph
# fork modification: 1. use local js script instead of downloading from remote server
#                    2. add logging 

import argparse
import base64
import json
import logging
from pathlib import Path
import re
import sys
import urllib.parse as urlparse
import time
import  os
import bs4
import langdetect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright
import requests

READABILITY_JS_COMMIT = "8e8ec27cd2013940bc6f3cc609de10e35a1d9d86"
READABILITY_JS_URL = f"https://raw.githubusercontent.com/mozilla/readability/{READABILITY_JS_COMMIT}"
REQUESTS_TIMEOUT = 10

# fork modification: use local js
LOCAL_JS=r'/home/fyl/project/PoliGraph/poligrapher/scripts/Readability.js'
LOCAL_JS2=r'/home/fyl/project/PoliGraph/poligrapher/scripts/Readability-readerable.js'

def get_readability_js():
    import os
    js_code = []
    js_path=LOCAL_JS if os.path.exists(LOCAL_JS) else ('./poligrapher/scripts/Readability.js')
    js_path2 = LOCAL_JS2 if os.path.exists(LOCAL_JS2) else ('./poligrapher/scripts/Readability-readerable.js')

    with open(js_path, 'r', encoding='utf-8') as f:
        js_code.append(f.read())
    with open(js_path2, 'r', encoding='utf-8') as f:
        js_code.append(f.read())
    return "\n".join(js_code)


def get_with_headers(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(url, headers=headers, timeout=REQUESTS_TIMEOUT)
        response.raise_for_status()
        return response.url
    except requests.exceptions.RequestException as e:
        logging.error("Request failed for %r: %s", url, e)
        return None


def url_arg_handler(url):
    parsed_url = urlparse.urlparse(url)

    # Not HTTP(s): interpret as a file path
    if parsed_url.scheme not in ["http", "https"]:
        parsed_path = Path(url).absolute()

        if not parsed_path.is_file():
            logging.error("File %r not found", url)
            return None

        return parsed_path.as_uri()

    # Handle Google Docs URLs
    if (parsed_url.hostname == "docs.google.com"
            and not parsed_url.path.endswith("/pub")
            and (m := re.match(r"/document/d/(1[a-zA-Z0-9_-]{42}[AEIMQUYcgkosw048])", parsed_url.path))):
        logging.info("Exporting HTML from Google Docs URL...")

        export_url = f"https://docs.google.com/feeds/download/documents/export/Export?id={m[1]}&exportFormat=html"

        req = requests.get(export_url)
        req.raise_for_status()

        base64_url = "data:text/html;base64," + base64.b64encode(req.content).decode()

        return base64_url

    # Handle other URLs: test with a HEAD request before starting browser
    logging.info("Testing URL %r with HEAD request", url)


    # Fork modification: use function get_with_headers instead of requests.head
    # try:
    #     requests.head(url, timeout=REQUESTS_TIMEOUT)
    # except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
    #     logging.error("Failed to connect to %r", url)
    #     logging.error("Error message: %s", e)
    #     return None
    # else:
    #     return url
    print("url:",url)
    access_url = get_with_headers(url)
    print("get_with_headers:",access_url)
    if not access_url:
        return None

    return access_url


# fork modification: block resources 
def block_resources(route, request):
    # remove useless resources
    if request.resource_type in  ['image', 'video', 'audio', 'font', 'stylesheet', 'manifest', 'media']:
        logging.info(f"Blocking resource: {request.url} of type {request.resource_type}")
        route.abort()
    else:
        route.continue_()

resource_timings = {}

def log_request(request):
    resource_timings[request.url] = {'start_time': time.time()}

def log_response(response):
    url = response.url
    if url in resource_timings and 'start_time' in resource_timings[url]:
        start_time = resource_timings[url]['start_time']
        load_time = time.time() - start_time
        resource_timings[url]['load_time'] = load_time
        logging.info(f"Response: {url} Status: {response.status} Load Time: {load_time:.2f}s")
    else:
        logging.warning(f"Unexpected response for {url}")

def log_request_failed(request):
    url = request.url
    logging.warning(f"Request failed: {url}")

def log_console(msg):
    logging.info(f"Console message: {msg.text}")

def log_frame_navigated(frame):
    if frame.parent_frame is None:
        logging.info(f"Frame navigated to: {frame.url}")


def main():
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Input URL or path")
    parser.add_argument("output", help="Output dir")
    parser.add_argument("--no-readability-js", action="store_true", help="Disable readability.js")
    args = parser.parse_args()

    access_url = url_arg_handler(args.url)

    if access_url is None:
        logging.error("URL failed pre-tests. Exiting...")
        sys.exit(-1)

    firefox_configs = {
        # Bypass CSP so we can always inject scripts
        "security.csp.enable": False,
        # Allow insecure TLS versions
        "security.tls.version.min": 1,
        "security.tls.version.enable-deprecated": True,
        # Prevent some background traffic
        "dom.serviceWorkers.enabled": False,
        "network.websocket.max-connections": 0,
        "media.autoplay.default": 5,
        "media.peerconnection.enabled": False,
        "privacy.trackingprotection.enabled": True,
        "privacy.trackingprotection.lower_network_priority": True,
        "privacy.trackingprotection.socialtracking.enabled": True,
    }

    # Firefox generates simpler accessibility tree than chromium
    # Tested on Debian's firefox-esr 91.5.0esr-1~deb11u1
    with sync_playwright() as p:
        browser = p.firefox.launch(firefox_user_prefs=firefox_configs)
        context = browser.new_context(bypass_csp=True)

        # Set route to filter resources
        context.on("route", block_resources)

        def error_cleanup(msg):
            logging.error(msg)
            if context:
                context.close()
            if browser:
                browser.close()
            sys.exit(-1)

        page = context.new_page()
        page.set_viewport_size({"width": 1080, "height": 1920})
        logging.info("Navigating to %r", access_url)

        # Record HTTP status and navigated URLs so we can check errors later
        url_status = dict()
        navigated_urls = []
        page.on("response", lambda r: url_status.update({r.url: r.status}))
        page.on("framenavigated", lambda f: f.parent_frame is None and navigated_urls.append(f.url))

        # fork modification: add request and response log
        # page.goto(access_url)
        # page.goto(access_url, wait_until="domcontentloaded")
        # try:
        #     # page.wait_for_load_state("networkidle")
        #     page.wait_for_load_state("domcontentloaded")
        # except PlaywrightTimeoutError:
        #     logging.warning("Cannot reach networkidle but will continue")

        try:
            # Try using 'networkidle' for 1 minute
            page.goto(access_url, wait_until="networkidle")
            page.wait_for_load_state("networkidle", timeout=60*1000)  # Wait for 1 minute
        except PlaywrightTimeoutError:
            logging.warning("Networkidle timeout after 1 minute. Switching to 3 mins.")
            try:
                # Finally, try using 'domcontentloaded' for 3 minutes
                # page.goto(access_url, wait_until="domcontentloaded")
                # page.wait_for_load_state("domcontentloaded", timeout=180 * 1000)  # Wait for 3 minutes
                page.goto(access_url, wait_until="domcontentloaded")
                page.wait_for_load_state("domcontentloaded", timeout=180 * 1000)  # Wait for 3 minutes
            except PlaywrightTimeoutError:
                logging.error("Failed to load page within the given 5 minutes time limits. Saving pure text and exit.")
                try:
                    save_pageText(access_url, args)

                except requests.exceptions.RequestException as e:
                    logging.error(f"Failed to fetch the page using requests: {e}")
                    error_cleanup("Failed to load page using Playwright and HTTP request.")

                # error_cleanup("Failed to load page within the given 5 mins time limits. Exiting.")



        # Check HTTP errors
        for url in navigated_urls:
            if (status_code := url_status.get(url, 0)) >= 400:
                error_cleanup(f"Got HTTP error {status_code}")

        # Apply readability.js
        page.evaluate("window.stop()")
        page.add_script_tag(content=get_readability_js())
        readability_info = page.evaluate(r"""(no_readability_js) => {
            window.stop();
    
            const documentClone = document.cloneNode(true);
            const article = new Readability(documentClone).parse();
            article.applied = false;
    
            document.querySelectorAll('[aria-hidden=true]').forEach((x) => x.setAttribute("aria-hidden", false));
    
            if (isProbablyReaderable(document) && !no_readability_js) {
                documentClone.body.innerHTML = article.content;
    
                if (documentClone.body.innerText.search(/(data|privacy|cookie)\s*(policy|notice)/) >= 0) {
                    document.body.innerHTML = article.content;
                    article.applied = true;
                }
            }
    
            for (const elem of document.querySelectorAll('script, link, style, header, footer, nav'))
                elem.remove();
    
            return article;
        }""", [args.no_readability_js])
        cleaned_html = page.content()

        # Check language
        soup = bs4.BeautifulSoup(cleaned_html, 'lxml')
        soup_text = soup.body.text if soup.body else ""

        try:
            lang = langdetect.detect(soup_text)
        except langdetect.lang_detect_exception.LangDetectException:
            lang = "UNKNOWN"

        if not lang.lower().startswith("en"):
            error_cleanup(f"Content language {lang} isn't English")

    #        if re.search(r"(data|privacy)\s*(?:policy|notice)", soup_text, re.I) is None:
    #        if re.search(r"data|privacy") is None and re.search(r"policy|notice|statement|claim") is None:
    #            error_cleanup("Not like a privacy policy")

        # obtain the accessibility tree
        snapshot = page.accessibility.snapshot(interesting_only=False)

        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True)

        with open(output_dir / "accessibility_tree.json", "w", encoding="utf-8") as fout:
            json.dump(snapshot, fout)

        with open(output_dir / "cleaned.html", "w", encoding="utf-8") as fout:
            fout.write(cleaned_html)
        logging.info(f"Saving cleaned html to {str(output_dir / 'cleaned.html')}")

        with open(output_dir / "readability.json", "w", encoding="utf-8") as fout:
            json.dump(readability_info, fout)

        # for modification: save pure page text.
        if not os.path.exists(output_dir / "pageText.txt"):
            try:
                save_pageText(access_url,args)
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to fetch the page using requests: {e}")
                error_cleanup("Failed to load page using Playwright and HTTP request.")

        logging.info("Saved to %s", output_dir)
        context.close()
        browser.close()


def save_pageText(access_url, args):
    response = requests.get(access_url)
    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    soup_text = soup.get_text()
    # save pure text
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "pageText.txt", "w", encoding="utf-8") as fout:
        fout.write(soup_text)
    logging.info(f"Text content saved to {output_dir / 'pageText.txt'}")


if __name__ == "__main__":
    main()