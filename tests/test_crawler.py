from bili_crawler.crawler import BiliCrawler


def test_run(BV):
    crawler = BiliCrawler(BV)
    crawler.run()


if __name__ == "__main__":
    BV = "BV1KxNPzSEhF"
    test_run(BV)
