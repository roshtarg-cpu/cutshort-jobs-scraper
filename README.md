# Cutshort Jobs Scraper

Scrape tech job listings from Cutshort.io (India's leading startup job platform) with full details including salaries, skills, company info, and more.

## Features

- 🎯 Extract job title, company, location, salary, experience, skills
- 🔄 Pagination support for large result sets
- 🌐 Residential proxy support for reliability
- 📊 Structured JSON output
- 🤖 Compatible with Claude, ChatGPT & AI agents via Apify MCP

## Input

- **startUrls**: URLs to scrape (default: https://cutshort.io/jobs)
- **maxResults**: Maximum jobs to scrape (default: 100)
- **proxyConfiguration**: Proxy settings (RESIDENTIAL recommended)

## Output

Each job listing includes:
- Job ID, title, company, location
- Salary range and experience requirements
- Required skills and tags
- Direct URL to job posting
- Scraped timestamp

## Example Output

```json
{
  "id": "625aea243de7d57305b12290",
  "title": "Senior Full Stack Developer",
  "company": "TechCorp India",
  "location": "Bangalore",
  "salary": "₹15-25 LPA",
  "experience": "3-5 years",
  "skills": ["React", "Node.js", "MongoDB"],
  "url": "https://cutshort.io/job/625aea243de7d57305b12290",
  "scrapedAt": "2026-08-19T03:35:00.000Z"
}
```

## Use Cases

- Tech recruitment and talent sourcing
- Salary benchmarking for Indian tech market
- Job market analysis and trends
- AI agent integration for automated job matching

Built for AI agents. Compatible with Claude Code, ChatGPT, and any MCP-enabled assistant.
