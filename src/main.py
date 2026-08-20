import asyncio
from datetime import datetime, timezone
from apify import Actor
from .utils import _fetch
from .parser import _extract_next_data, parse_jobs

async def main():
    async with Actor:
        # Get input
        actor_input = await Actor.get_input() or {}
        max_results = actor_input.get('maxResults', 50)
        skill_keyword = actor_input.get('skillKeyword', 'python')
        location = actor_input.get('location', 'bangalore')
        proxy_config = actor_input.get('proxyConfiguration')
        
        # Construct URL based on inputs
        if location:
            # https://cutshort.io/jobs/python-jobs-in-bangalore
            url = f'https://cutshort.io/jobs/{skill_keyword}-jobs-in-{location}'
        else:
            # https://cutshort.io/jobs/python-jobs (all India)
            url = f'https://cutshort.io/jobs/{skill_keyword}-jobs'
        
        Actor.log.info(f'Starting scrape from: {url} (maxResults={max_results})')
        
        # Get proxy URL - FIX: await the create_proxy_configuration
        proxy_url = None
        if proxy_config:
            try:
                proxy_conf = await Actor.create_proxy_configuration(actor_proxy_input=proxy_config)
                proxy_url = await proxy_conf.new_url()
                Actor.log.info(f'Using proxy: {proxy_url.split("@")[1] if "@" in proxy_url else "configured"}')
            except Exception as e:
                Actor.log.warning(f'Proxy setup failed: {e}')
        
        total_scraped = 0
        
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
            return  # Exit early if fetch failed
        
        # Save HTML for debugging
        Actor.log.info(f'HTML size: {len(html)} bytes')
        
        # Extract __NEXT_DATA__
        next_data = _extract_next_data(html)
        if not next_data:
            Actor.log.error('Could not extract __NEXT_DATA__')
            # Save HTML sample for debugging
            Actor.log.info(f'HTML sample: {html[:1000]}')
            return  # Exit early if parsing failed
        
        # Log structure for debugging
        Actor.log.info(f'__NEXT_DATA__ keys: {list(next_data.keys())}')
        
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
        
        Actor.log.info(f'✅ Scraping complete! Total jobs: {total_scraped}')
