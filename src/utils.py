import re
import os
from camoufox.async_api import AsyncCamoufox
from apify import Actor

def _parse_proxy(proxy_url):
    """Parse Apify proxy URL into components."""
    if not proxy_url:
        return None
    match = re.match(r'http://([^:]+):([^@]+)@([^:]+):(\d+)', proxy_url)
    if not match:
        return None
    username, password, host, port = match.groups()
    return {
        'server': f'http://{host}:{port}',
        'username': username,
        'password': password
    }

async def _fetch(url, proxy_url=None):
    """Fetch URL using Camoufox with geoip and return HTML."""
    proxy_config = _parse_proxy(proxy_url) if proxy_url else None
    
    try:
        async with AsyncCamoufox(
            headless=True,
            geoip=True,
            proxy=proxy_config
        ) as browser:
            page = await browser.new_page()
            try:
                response = await page.goto(url, wait_until='networkidle', timeout=90000)
                # Wait for content to load
                await page.wait_for_timeout(3000)
                
                html = await page.content()
                
                # Validate response
                if not response or response.status >= 400:
                    Actor.log.warning(f'Bad response status: {response.status if response else "None"}')
                    return None
                    
                if len(html) < 500:
                    Actor.log.warning(f'Response too small: {len(html)} bytes')
                    return None
                    
                return html
                
            finally:
                await page.close()
                
    except Exception as e:
        Actor.log.error(f'Fetch error for {url}: {e}')
        return None
