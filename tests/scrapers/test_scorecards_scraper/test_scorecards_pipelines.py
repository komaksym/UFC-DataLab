import pytest
import scrapy.pipelines
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from scrapy.http import Request
from src.scraping.ufc_scorecards_scraping. \
     ufc_scorecards_scraping.pipelines import ScorecardImagesPipeline
from src.scraping.ufc_scorecards_scraping. \
     ufc_scorecards_scraping.items import ScorecardImagesItem
from src.scraping.ufc_scorecards_scraping.ufc_scorecards_scraping. \
     spiders.scorecards_spider import Scorecards_Spider


class TestScorecardImagesPipeline:
    def setup_method(self) -> None:
        self.pipeline: ScorecardImagesPipeline = ScorecardImagesPipeline("downloaded_images")
        self.item: ScorecardImagesItem = ScorecardImagesItem()
        self.item_processed: ScorecardImagesItem = ScorecardImagesItem()
        self.info: scrapy.pipelines.media.MediaPipeline.SpiderInfo = \
            scrapy.pipelines.media.MediaPipeline.SpiderInfo(Scorecards_Spider())

        self.mock_scorecard: str
        self.mock_results: List[Tuple[bool, Dict[str, str]]]

        def create_full_path(relative_path: str) -> str:
            """Method for finding paths to mock pages"""
            full_path = Path(__file__).parents[0] / relative_path
            return f"file://{full_path.resolve()}"
        
        self.mock_scorecard = create_full_path('mock_pages/mock_scorecard/mock_scorecard.avif')

    @pytest.fixture
    def mock_urls_raw(self) -> None:
        self.item['image_urls'] = ['https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_rodriguez-def-knutsson.png?itok=jvvraYfK',
                                    'https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_grant-def-taveras.png?itok=8F0l_pQB',
                                    'https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_maverick-def-horth.png?itok=Ek0Zj8M2',
                                    'https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_felipe-def-johns.png?itok=2UDEGvUC',
                                    'https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_woodson-def-padilla.png?itok=uvJ7nZDF',
                                    'https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_alvarez-def-klose.png?itok=oXVLu4QD',
                                    'https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_johnson-def-azaitar.png?itok=s5ag3ZHt',
                                    'https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_stirling-def-tokkos.png?itok=oxQs_Qq9',
                                    'https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_yanez-vs-marcos.png?itok=rdQKMQln',
                                    'https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_jacoby-def-petrino.png?itok=R3Lr0-Z3',
                                    'https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_kape-def-silva.png?itok=IxLVrcEd',
                                    'https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_swanson-def-quarantillo.png?itok=TXw-FZWN',
                                    'https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_buckley-def-covington.png?itok=-n6FjYei']
    
    def test_get_media_requests(self, mock_urls_raw: None) -> None:
        responses: List[Request] = list(self.pipeline.get_media_requests(self.item, self.info))

        assert all(isinstance(response, scrapy.Request) for response in responses)

    def test_file_path(self) -> None:
        response: str = self.pipeline.file_path(scrapy.Request(self.mock_scorecard,
                                                               meta={"img_index": 0}))
        assert response == 'downloaded_images/0.jpg'

    @pytest.fixture
    def mock_item_raw(self) -> None:
        self.mock_results = [(True, {'url': 'https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_rodriguez-def-knutsson.png?itok=jvvraYfK', 'path': 'downloaded_images/0.jpg', 'checksum': '58190df6c026d020f4f7f71a9ef18a9d', 'status': 'uptodate'})]
        self.item['image_urls'] = 'https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_rodriguez-def-knutsson.png?itok=jvvraYfK'

    @pytest.fixture
    def mock_item_processed(self) -> None:
        self.item_processed['image_urls'] = 'https://ufc.com/images/styles/inline/s3/2024-12/121424-ufc-fight-night-tampa-scorecards_rodriguez-def-knutsson.png?itok=jvvraYfK'
        self.item_processed['images'] = ['downloaded_images/0.jpg']

    def test_item_completed(self, mock_item_raw: None, mock_item_processed: None) -> ScorecardImagesItem:
        response: ScorecardImagesItem = self.pipeline.item_completed(
            self.mock_results, self.item, self.info)
        assert response == self.item_processed
