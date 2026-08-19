import json
import re
from apify import Actor

def _extract_next_data(html):
    """Extract __NEXT_DATA__ JSON from HTML."""
    try:
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)
        if not match:
            Actor.log.warning('__NEXT_DATA__ not found in HTML')
            return None
            
        data = json.loads(match.group(1))
        return data
        
    except Exception as e:
        Actor.log.error(f'Error extracting __NEXT_DATA__: {e}')
        return None

def parse_jobs(next_data):
    """Parse job listings from __NEXT_DATA__."""
    jobs = []
    
    try:
        # Navigate through Next.js data structure
        # Based on sample: props.pageProps.dehydratedState.queries[].state.data[]
        queries = next_data.get('props', {}).get('pageProps', {}).get('dehydratedState', {}).get('queries', [])
        
        for query in queries:
            state_data = query.get('state', {}).get('data', [])
            
            if isinstance(state_data, list):
                for item in state_data:
                    if isinstance(item, dict) and '_id' in item:
                        # Extract job data
                        job = {
                            'id': item.get('_id'),
                            'title': item.get('title', item.get('role', {}).get('name')),
                            'company': item.get('company', {}).get('name') if isinstance(item.get('company'), dict) else None,
                            'location': item.get('location', {}).get('name') if isinstance(item.get('location'), dict) else item.get('location'),
                            'experience': item.get('experience'),
                            'salary': item.get('salary'),
                            'skills': item.get('skills', []),
                            'tags': item.get('tags', []),
                            'description': item.get('description'),
                            'postedDate': item.get('createdAt', item.get('postedDate')),
                            'jobType': item.get('jobType'),
                            'url': f"https://cutshort.io/job/{item.get('_id')}" if item.get('_id') else None,
                            'companyId': item.get('userId', {}).get('_id') if isinstance(item.get('userId'), dict) else None,
                            'scrapedAt': None  # Will be set in main
                        }
                        jobs.append(job)
        
        Actor.log.info(f'Parsed {len(jobs)} jobs from __NEXT_DATA__')
        return jobs
        
    except Exception as e:
        Actor.log.error(f'Error parsing jobs: {e}')
        return []
