import asyncio
from datetime import datetime, timezone
from apify import Actor
from .utils import _fetch
from .parser import _extract_next_data, parse_jobs

async def main():
    async with Actor:
        # Get input
        actor_input = await Actor.get_input() or {}
        max_results = actor_input.get('maxResults', 100)
        start_urls = actor_input.get('startUrls', [{'url': 'https://cutshort.io/jobs'}])
        proxy_config = actor_input.get('proxyConfiguration')
        
        Actor.log.info(f'Starting scrape with maxResults={max_results}')
        
        # Get proxy URL
        proxy_url = None
        if proxy_config:
            try:
                proxy_url = await Actor.create_proxy_configuration(
                    actor_proxy_input=proxy_config
                ).new_url()
                Actor.log.info(f'Using proxy: {proxy_url.split("@")[1] if "@" in proxy_url else "configured"}')
            except Exception as e:
                Actor.log.warning(f'Proxy setup failed: {e}')
        
        total_scraped = 0
        
        # Process each start URL
        for url_obj in start_urls:
            url = url_obj.get('url', 'https://cutshort.io/jobs')
            Actor.log.info(f'Fetching: {url}')
            
            # Retry logic
            html = None
            for attempt in range(3):
                html = await _fetch(url, proxy_url)
                if html:
                    break
                Actor.log.warning(f'Attempt {attempt+1}/3 failed, retrying...')
                await asyncio.sleep(2 * (attempt + 1))
            
            if not html:
                Actor.log.error(f'Failed to fetch {url} after 3 attempts')
                continue
            
            # Extract __NEXT_DATA__
            next_data = _extract_next_data(html)
            if not next_data:
                Actor.log.error('Could not extract __NEXT_DATA__')
                continue
            
            # Parse jobs
            jobs = parse_jobs(next_data)
            
            # Add timestamp and push to dataset
            scraped_at = datetime.now(timezone.utc).isoformat()
            
            for job in jobs:
                if total_scraped >= max_results:
                    break
                    
                job['scrapedAt'] = scraped_at
                
                # Push to dataset immediately
                await Actor.push_data(job)
                total_scraped += 1
                
                if total_scraped % 10 == 0:
                    Actor.log.info(f'Scraped {total_scraped} jobs so far...')
            
            if total_scraped >= max_results:
                break
        
        Actor.log.info(f'✅ Scraping complete! Total jobs: {total_scraped}')
