import urllib.request
import urllib.parse
import re
import time
from concurrent.futures import ThreadPoolExecutor


class SitemapBuilder:
    def __init__(self, base_url, max_depth=None):
        self.base_url = base_url
        self.max_depth = max_depth
        self.visited_links = set()
        self.structure = {}
        self.original_domain = self.extract_domain(base_url)

    def build_sitemap(self):
        start_time = time.time()

        with ThreadPoolExecutor() as executor:
            self.crawl_page(self.base_url, executor)

        end_time = time.time()
        time_consumed = end_time - start_time

        return time_consumed, len(self.visited_links), self.structure

    def crawl_page(self, url, executor, depth=2):
        if self.max_depth is not None and depth > self.max_depth:
            return

        if url in self.visited_links:
            return
        print(url)
        self.visited_links.add(url)
        response = urllib.request.urlopen(url)
        html = response.read().decode('utf-8')
        links = self.extract_links(html)

        self.structure[url] = links

        results = []
        for link in links:
            absolute_link = urllib.parse.urljoin(url, link)
            if absolute_link not in self.visited_links:  # Skip already visited URLs
                if self.is_same_domain(absolute_link):
                    results.append(executor.submit(self.crawl_page, absolute_link, executor, depth + 1))

        for result in results:
            result.result()

    def extract_links(self, html):
        link_pattern = re.compile(r'<a\s(?:.*?\s)*?href=[\'"](.*?)[\'"].*?>')
        links = re.findall(link_pattern, html)
        print('Links: ', links)
        filtered_links = []
        for link in links:
            if link.startswith(('http://', 'https://', '/', './')):
                filtered_links.append(link)

        return filtered_links

    def extract_domain(self, url):
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc
        return domain

    def is_same_domain(self, url):
        domain = self.extract_domain(url)
        return domain == self.original_domain or domain.endswith('.' + self.original_domain)
