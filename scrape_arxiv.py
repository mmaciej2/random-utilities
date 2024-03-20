#!/usr/bin/env python3

import sys, os
import urllib.request as libreq
import ssl
import feedparser
import datetime
import subprocess
ssl._create_default_https_context = ssl._create_unverified_context

#################### Parameters to set ####################

search_terms = ['speech separation', 'diarization', 'speech enhancement']
output_directory = '/Users/mattmaciejewski/Documents/Webpages/arXiv_scraper/'
time_delta = datetime.timedelta(weeks=1)
auto_open = True

###########################################################

base_url = 'https://export.arxiv.org/api/query?search_query='+'+OR+'.join([f'all:"{term}"'.replace(' ','%20') for term in search_terms])+'&sortBy=submittedDate&sortOrder=descending'

not_done = True
articles = []
scrape_counter = 0
now = datetime.datetime.now(datetime.timezone.utc)
before = now - time_delta
while not_done:  # keeps grabbing most recent articles until they are too old
    url = base_url + f'&start={scrape_counter*10}&max_results=10'
    with libreq.urlopen(url) as urlF:
        feed = feedparser.parse(urlF.read())
    for entry in feed.entries:
        pubtime = datetime.datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        if pubtime > before:
            title = entry.title.replace('\n  ', ' ')
            for link in entry.links:
                if link.rel == 'alternate':
                    hyperlink = link.href
            authors = ', '.join(author.name for author in entry.authors)
            articles.append([title, authors, pubtime.strftime("%Y-%m-%d"), hyperlink])
        else:
            not_done = False
    scrape_counter += 1

# Write html file
output_file = os.path.join(output_directory, before.strftime("%Y%m%d")+'-'+now.strftime("%Y%m%d")+'.html')
with open(output_file, 'w') as outF:
    outF.write('<!DOCTYPE html>\n')
    outF.write('<html>\n')
    outF.write('<body>\n')
    outF.write(f'<h1>Articles {before.strftime("%Y-%m-%d")} to {now.strftime("%Y-%m-%d")}</h1>\n')
    outF.write('<p>\n  <b>Search terms:</b><br>\n  ')
    outF.write('<br>\n  '.join(search_terms))
    outF.write('\n</p>')
    if len(articles) == 0:
        outF.write('<p>None</p>\n')
    for article in articles:
        outF.write('<p>\n')
        outF.write(f'  <a target="_blank" rel="noopener noreferrer" href="{article[3]}"><b>{article[0]}</b></a><br>\n')
        outF.write(f'  {article[1]}<br>\n')
        outF.write(f'  {article[2]}\n')
        outF.write('</p>\n')
    outF.write('</body>\n')
    outF.write('</html>')

if auto_open:
    subprocess.Popen(['open', output_file])
