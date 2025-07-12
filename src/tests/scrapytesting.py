import asyncio
from twisted.internet import asyncioreactor
asyncioreactor.install()

from scrapy import Spider, Request, exceptions
from twisted.internet import reactor
from scrapy.crawler import Crawler, CrawlerRunner, CrawlerProcess
import random
import time

from scrapy.utils.project import get_project_settings

from multiprocessing import Process

import warnings
warnings.filterwarnings("ignore", category=exceptions.ScrapyDeprecationWarning)

class MySpider(Spider):
    name = "MySpider"
    
    def start_requests(self):
        print("start_requests()")
        yield Request("https://bestmods.io", self.parse)
    
    def parse(self, resp):
        print("parse()")
        print(resp)
        
class MySpiderProcess(Process):
    runner = None
    
    def __init__(self):
        super().__init__()
    
    def start(self):
        super().start()
        self.runner = CrawlerProcess(get_project_settings())
        self.runner.crawl(MySpider)
        self.runner.start(stop_after_crawl=True)
        
def executor():
    settings = get_project_settings()
    settings.set("logging", 0)
    
    crawler = CrawlerProcess(settings)
    crawler.crawl(MySpider)
    crawler.start()
    
def main():
    print("Starting crawler")
    
    while True:
        k = Process(target=executor)
        k.start()
        print(k)
        
        print("Delaying...")
            
        delay = random.randint(5, 10)
        time.sleep(delay)
        
        print(k)    
if __name__ == "__main__":
    main()