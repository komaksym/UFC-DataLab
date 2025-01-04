import pytest
from scrapy.http import Request, TextResponse
from ufcstats_scraping.spiders.stats_spider import Stats_Spider
import os


def fake_response_from_file(file_name, url=None):
    """Create a Scrapy fake HTTP response from a HTML file"""
    if not url:
        url = 'http://ufcstats.com/fake'

    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', file_name)
    
    with open(file_path, 'r') as f:
        file_content = f.read()

    return TextResponse(url=url, 
        body=file_content.encode('utf-8'), 
        encoding='utf-8')


class TestStatsSpider:

    def setup_method(self):
        self.spider = Stats_Spider()

    def test_parse_event_list(self):
        response = fake_response_from_file('event_list.html')
        results = list(self.spider.parse(response))
        
        # Test that we get the correct number of requests
        assert len(results) > 0
        assert all(isinstance(r, Request) for r in results)
        # Test that URLs are properly formatted
        assert all('ufcstats.com/event-details' in r.url for r in results)

    def test_parse_event(self):
        response = fake_response_from_file('event_page.html')
        results = list(self.spider.parse_event(response))
        
        # Test that we get the correct number of fight requests
        assert len(results) > 0
        assert all(isinstance(r, Request) for r in results)
        
        # Test event data is properly extracted
        event_data = results[0].meta['event_data']
        assert 'name' in event_data
        assert 'date' in event_data
        assert 'location' in event_data

    def test_parse_fight(self):
        response = fake_response_from_file('fight_page.html')
        response.meta['event_data'] = {
            'name': 'UFC Test Event',
            'date': '2023-01-01',
            'location': 'Test Location'
        }
        
        results = list(self.spider.parse_fight(response))
        
        # Test that we get exactly one fight item
        assert len(results) == 1
        fight_item = results[0]
        
        # Test critical fields
        assert fight_item['red_fighter_name']
        assert fight_item['blue_fighter_name']
        assert fight_item['method']
        assert fight_item['event_name'] == 'UFC Test Event'

    def test_error_handling(self):
        response = fake_response_from_file('invalid_fight.html')
        response.meta['event_data'] = {
            'name': 'UFC Test Event',
            'date': '2023-01-01',
            'location': 'Test Location'
        }
        
        # Test that invalid data returns None
        results = list(self.spider.parse_fight(response))
        assert len(results) == 0
