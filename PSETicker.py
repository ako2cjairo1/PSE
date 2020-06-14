import os
import requests
import json
import time
from colorama import init

URL = "https://phisix-api3.appspot.com/"
SPACE_ALIGNMENT = 20


class PSE_Ticker:
    def __init__(self, stocks):
        self.stocks_list = stocks
        self.watch_list = []
        self.is_watchlist = False

    def fetch_stocks_json(self):
        print(f"\n**Fetching stock updates from {URL}")
        # get json data from api
        response = requests.get(f"{URL}stocks.json")
        time.sleep(3)

        # write the response data to a file (JSON format)
        with open("stocks.json", "w") as file_write:
            file_write.write(response.text)

        # read the created json file and append stocks data to stocks_list
        with open("stocks.json", "r") as file_read:
            data = json.load(file_read)
            self.stocks_list = [stock for stock in data["stock"]]
        print("DONE\n")

    def create_watch_list(self, code_csv):
        if code_csv:
            self.watch_list = code_csv.lower().split(",")

    def run_ticker(self):
        # initialize foreground coloring
        init(autoreset=True)

        # clear the console screen
        os.system("cls")

        if len(self.stocks_list) < 1:
            print("\n**No list of stock codes to show\n")
            return

        if self.is_watchlist:
            self.stocks_list = [stock for stock in self.stocks_list if stock["symbol"].strip(
            ).lower() in self.watch_list]

        while True:
            if self.is_watchlist:
                print("* WATCHLIST MODE *".center(SPACE_ALIGNMENT, " "), "\n")
            for stock in self.stocks_list:
                percent_change = float(stock["percent_change"])

                # determine text color depending on percent_change value
                # red: negative value, green: positive value, yellow: no change or zero value
                color_code = "\033[22;31;40m" if percent_change < 0 else (
                    "\033[1;32;40m" if percent_change > 0 else "\033[22;33;40m")

                print(
                    f"{color_code}{stock['symbol'].strip().upper().center(SPACE_ALIGNMENT, ' ')}")
                print(
                    f"{color_code}{str(stock['price']['amount']).center(SPACE_ALIGNMENT, ' ')}")
                print(
                    f"{color_code}{str(stock['volume']).center(SPACE_ALIGNMENT, ' ')}\n")
                time.sleep(1)
