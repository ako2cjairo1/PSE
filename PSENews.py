import requests
import urllib.parse as parser
import json
from bs4 import BeautifulSoup
from colorama import init
import time

SPACE_ALIGNMENT = 100
TIME_TO_CHECK_NEWS = 360  # an hour (3600 secs divide to 10)


class PSE_News:
    def __init__(self):
        self.pse_news = []
        self.fetch_news()

    def fetch_news(self):
        response = requests.get(
            "https://www.feedspot.com/news/philippines_stock_market")

        # remove and replace unecessary tags, chars, etc. here
        res = response.text.replace(
            "title=\"<h4>", "story-preview=\"<h4>")

        soup = BeautifulSoup(res, "html.parser")

        # find the "most recent" section div tag
        most_recent_soup = soup.find_all(
            "div", {"class": "col-xs-12 col-md-4"})[0]

        # find all headlines in "most recent" section
        headlines_soup = most_recent_soup.find_all(
            "a", {"class": "one-line-ellipsis col-md-10 col-sm-10 col-xs-10"})

        # loop through each headlines to build json format dictionary
        headlines = []
        for headline in headlines_soup:
            title = headline.text.strip()
            url = headline["href"]
            story_preview = headline["story-preview"].split(
                "<br><br>")[-1].replace("\xa0", " ").strip()

            headlines.append({
                "headline": f"{title}",
                "url": f"{url}",
                "story_preview": f"{story_preview}",
            })

        # create the json file type
        with open("PSE_news.json", "w", encoding="utf-8") as fw:
            news = {
                "news": headlines
            }
            fw.write(str(news).replace("'", "\""))

        self.pse_news = headlines
        return self.pse_news

    def create_news_banner(self, headline):
        title_color = "\033[2;30;47m"
        source_color = "\033[1;36;49m"
        color_reset = "\033[0;39;49m"

        title = "{} {} ".format(title_color, headline["headline"])
        url = parser.urlparse(headline["url"]).netloc
        url = "{} {}".format(source_color, url)
        summary = "{} {} ".format(color_reset, headline["story_preview"])

        print(title)
        print("{}more on{}".format(summary, url), "\n")

    def show_news_banner(self):
        tick_count = 0

        self.fetch_news()

        if len(self.pse_news) < 1:
            # return immediately if no list of headlines to show
            print("\n**No new headlines on PH Business News.\n")
            return

        # initialize text coloring
        init(autoreset=True)
        print("\n")

        while True:
            # loop through the list of headlines to present
            for headline in self.pse_news:
                self.create_news_banner(headline)

                time.sleep(10)
                tick_count += 1

                if tick_count >= TIME_TO_CHECK_NEWS:
                    self.show_news_banner()
