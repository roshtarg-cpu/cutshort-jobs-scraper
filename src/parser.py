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
        queries = next_data.get('props', {}).get('pageProps', {}).get('dehydratedState', {}).get('queries', [])
        
        Actor.log.info(f'Found {len(queries)} queries in __NEXT_DATA__')
        
        for query in queries:
            query_key = query.get('queryKey', [])
            state_data = query.get('state', {}).get('data', {})
            
            # Look for job data in nested structure
            # Can be at: data.data.pageData.jobs (featured jobs page)
            # Or: state.data[] directly (some other pages)
            
            if isinstance(state_data, dict):
                # Try: data.data.pageData.jobs
                nested_data = state_data.get('data', {})
                if isinstance(nested_data, dict):
                    page_data = nested_data.get('pageData', {})
                    if isinstance(page_data, dict) and 'jobs' in page_data:
                        job_items = page_data['jobs']
                        Actor.log.info(f'Found {len(job_items)} jobs in query {query_key}')
                        
                        for item in job_items:
                            if not isinstance(item, dict) or '_id' not in item:
                                continue
                                
                            # Extract salary range
                            salary_range = item.get('salaryRange', {})
                            if isinstance(salary_range, dict):
                                min_sal = salary_range.get('minVanity', 0)
                                max_sal = salary_range.get('maxVanity', 0)
                                currency = salary_range.get('currency', 'INR')
                                # Convert to lakhs
                                salary = f"{currency} {min_sal/100000:.1f}-{max_sal/100000:.1f} LPA" if min_sal and max_sal else None
                            else:
                                salary = item.get('salaryRangeText')
                            
                            # Extract company details
                            company_details = item.get('companyDetails', {})
                            company_name = company_details.get('name') if isinstance(company_details, dict) else None
                            
                            # Extract experience range
                            exp_range = item.get('expRange', {})
                            if isinstance(exp_range, dict):
                                min_exp = exp_range.get('min', 0)
                                max_exp = exp_range.get('max', 0)
                                experience = f"{min_exp}-{max_exp} years" if max_exp else None
                            else:
                                experience = None
                            
                            # Extract locations
                            locations = item.get('locations', [])
                            location = item.get('locationsText') or (locations[0] if locations else None)
                            
                            job = {
                                'id': item.get('_id'),
                                'title': item.get('headline'),
                                'company': company_name,
                                'location': location,
                                'experience': experience,
                                'salary': salary,
                                'skills': item.get('allSkills', []),
                                'tags': [],
                                'description': item.get('sanitizedComment'),
                                'postedDate': item.get('createdAt'),
                                'jobType': item.get('remoteType'),
                                'url': item.get('publicUrl'),
                                'companyId': item.get('companyId'),
                                'scrapedAt': None  # Will be set in main
                            }
                            jobs.append(job)
        
        Actor.log.info(f'Parsed {len(jobs)} total jobs from __NEXT_DATA__')
        return jobs
        
    except Exception as e:
        Actor.log.error(f'Error parsing jobs: {e}')
        import traceback
        Actor.log.error(traceback.format_exc())
        return []
