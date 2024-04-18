import os
import sys
current_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(current_directory, "modules"))
sys.path.append(os.path.join(current_directory, "config"))

import requests
import base64
import time
import shutil
import zipfile
import re
import threading


from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from pdf2image import convert_from_path
from urllib.parse import urlparse
from colorama import Fore, Style, init
from threading import Lock



import requests
import threading
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from pprint import pprint, pformat
from collections import defaultdict
from seleniumbase import Driver
from pdf_generator import PDFGenerator
import os
YELLOW = "\033[33m"
RESET = "\033[0m"
BLUE = "\033[34m"
GREEN = "\033[32m"
PURPLE = "\033[35m" 
def sanitize_path(path):
    original_path = path  # Debugging output
    masked_original_path = f"...{path[20:]}" if len(path) > 20 else path
    sanitized_path  = path.replace(r'https:\\', '_')
    sanitized_path  = sanitized_path .replace(r'https:/', '_')
    sanitized_path  = sanitized_path .replace(r'https://', '_')
    sanitized_path  = sanitized_path .replace(r'http://', '_')

    sanitized_path  = sanitized_path .replace(':', '') 
    if sanitized_path  != original_path:
        masked_sanitized_path = f"...{sanitized_path[20:]}" if len(sanitized_path) > 20 else sanitized_path
        print(f"Sanitized path from {original_path} to {PURPLE}{masked_sanitized_path}{RESET}")
    return sanitized_path 
class DocScrapper():
    def __init__(self):
        self.output_dir = "output"
        self.output_pdf_dir = os.path.join(self.output_dir, "pdf")
        self.output_pdf_to_images_dir = os.path.join(self.output_dir, "pdf_to_images")
        self.output_pdf_file = "output_pdf.pdf"
        self.output_images = os.path.join(self.output_dir, "images")
        self.output_webscrapping_dir = os.path.join(self.output_dir, "webscrapping")
        self.output_webscrapping_link_file = "all_links.txt"
        self.output_webscrapping_subdomain_file = "all_subdomains.txt"
        self.page_source_dir = os.path.join(self.output_dir, "page_source")
        self.page_source_counter = 1
        self.driver = Driver(uc=True)
        self.driver.set_window_position(-1920,0, windowHandle='current')
        self.driver.maximize_window()
        self.pdf_generator = PDFGenerator(self.driver, self.output_pdf_dir, self.output_pdf_file)
    
    def save_as_pdf(self, output_path, url):
        masked_url = f"...{url[20:]}" if len(url) > 20 else url
        masked_path = f"...{output_path[20:]}" if len(output_path) > 20 else output_path
        
        output_path = sanitize_path(output_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        output_file = os.path.join(output_path, '.pdf')
        main_content = self.driver.execute_script("return document.querySelector('main').outerHTML;")
        escaped_main_content = main_content.replace('`', '\\`').replace('${', '\\${')
        self.driver.execute_script("window.tempContent = arguments[0];", escaped_main_content)
        self.driver.execute_script("document.body.innerHTML = window.tempContent;")

        print_params = {
            "landscape": False,
            "displayHeaderFooter": False,
            "printBackground": True,
            "preferCSSPageSize": True,
            "scale" : 0.5
        }
        result = self.driver.execute_cdp_cmd("Page.printToPDF", print_params)
        with open(output_file, "wb") as f:
            f.write(base64.b64decode(result["data"]))
        print(f"Saved {BLUE}{masked_url}{RESET} as {GREEN}{masked_path}{RESET}")
    
    def extract_links_from_url(self, base_url):
        
        source = self.driver.page_source
        self.soup = BeautifulSoup(source, 'html.parser')        
        links = self.soup.find_all('a')

        urls = set()
        for link in links:
            href = link.get('href')
            if href and href.startswith("/"):
                href = base_url.rstrip('/') + href
            elif href and base_url in href:
                urls.add(href)
            elif 'html' in href:
                urls.add(base_url + href)
                
            else:
                print(f"Skipping {YELLOW}{href}{RESET}")
                continue

        return urls
    

    def scrape(self, base_url = 'https://docs.tweepy.org/'):
            to_fetch = base_url
            if not isinstance(to_fetch, list):
                to_fetch = [to_fetch]
            visited_urls = set()
            domain = urlparse(base_url).netloc
            try:
                while to_fetch:
                    url = to_fetch.pop()
                    if url in visited_urls:
                        continue

                    visited_urls.add(url)
                    self.driver.get(url)
                    time.sleep(1)
                    current_url = self.driver.current_url # Get the current URL after the page has loaded to handle redirects
                    

                    new_urls = [u for u in self.extract_links_from_url(current_url) if urlparse(u).netloc == domain and u not in visited_urls]
                    to_fetch.extend([u for u in new_urls if u not in visited_urls])

                    segments = [segment.replace('.', '-') for segment in url.rstrip('/').split('/')[3:]]
                    if segments:
                        path = os.path.join("output_pdf", *segments)
                    else:
                        path = "output_pdf"

                    self.save_as_pdf(path, url)


                    # Post-process the files
                    #post_process_files()

                    # Zip the entire output directory
                    #zip_output_directory()
 

            finally:
                self.driver.quit()



     
def main():
    docscrapper = DocScrapper()
    docscrapper.scrape(base_url = 'https://docs.tweepy.org/')


if __name__ == "__main__":
    main()
