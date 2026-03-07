import requests
from bs4 import BeautifulSoup
import csv

def get_hn_jobs():
    url = "https://news.ycombinator.com/jobs"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("Fetching jobs from Hacker News...")
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html5lib')
    
    jobs = []
    
    job_rows = soup.find_all('tr', class_='athing')
    
    print(f"Found {len(job_rows)} job posts")
    
    for job in job_rows[:20]:
        try:
            titleline = job.find('span', class_='titleline')
            if not titleline:
                continue
            
            link_elem = titleline.find('a')
            if not link_elem:
                continue
            
            title = link_elem.get_text(strip=True)
            job_url = link_elem.get('href', '')
            
            if job_url.startswith('item?'):
                job_url = "https://news.ycombinator.com/" + job_url
            elif not job_url.startswith('http'):
                job_url = "https://news.ycombinator.com/" + job_url
            
            company = "Unknown"
            if ':' in title:
                parts = title.split(':', 1)
                company = parts[0].strip()
                title = parts[1].strip()
            
            jobs.append({
                'Company': company,
                'Title': title,
                'URL': job_url
            })
            
            print(f"  {company} | {title[:50]}...")
            
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    return jobs

jobs = get_hn_jobs()

if jobs:
    with open('hn_jobs.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Company', 'Title', 'URL'])
        writer.writeheader()
        writer.writerows(jobs)
    
    print(f"\nSaved {len(jobs)} jobs to hn_jobs.csv!")
    
    print("\nSample jobs:")
    for i, job in enumerate(jobs[:5], 1):
        print(f"{i}. {job['Company']} - {job['Title'][:60]}...")
else:
    print("\nNo jobs found")