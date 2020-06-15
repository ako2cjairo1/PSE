try:
    import os
    import requests
    import json
    import time
    import datetime as dt
    from colorama import init
except:
    print("Some importing libraries are not found.")

URL = "https://phisix-api3.appspot.com/"
SPACE_ALIGNMENT = 20
TIME_TO_CHECK_NEW_DATA = 10


class PSE_Ticker:
    def __init__(self, stocks):
        self.stocks_list = stocks
        self.as_of = ""
        self.watch_list = []
        self.is_watchlist = False

    def fetch_stocks_json(self):
        response = None
        response_as_of = None

        try:
            # get json data from api
            response = requests.get(f"{URL}stocks.json")
            # time.sleep(3)

            if response:
                # save the time stamp of json data we got from get request
                response_as_of = json.loads(response.text)["as_of"]
        except:
            print("\n**Update failed, we'll try again after a moment.\n")

        # if not the same date/time stamp save the new data to json file
        if response_as_of and self.as_of != response_as_of:
            # write the response data to a file (JSON format)
            with open("stocks.json", "w") as file_write:
                file_write.write(response.text)

        if os.path.isfile("stocks.json"):
            # read the created json file
            with open("stocks.json", "r") as file_read:
                data = json.load(file_read)

                self.as_of = data["as_of"]
                if self.is_watchlist:
                    # append only stocks that are on the watch_list
                    self.stocks_list = [stock for stock in data["stock"] if stock["symbol"].strip(
                    ).lower() in self.watch_list]
                else:
                    # append ALL stocks data to stocks_list
                    self.stocks_list = [stock for stock in data["stock"]]

            if len(self.stocks_list) < 1:
                print("\n**No list of stock codes to show\n")

    def create_watch_list(self, code_csv):
        if code_csv:
            self.watch_list = code_csv.lower().split(",")

    def run_ticker(self):
        tick_count = 0
        # initialize text coloring
        init(autoreset=True)

        # clear the console screen
        os.system("cls")

        while True:
            if self.is_watchlist:
                print("* WATCHLIST MODE *".center(SPACE_ALIGNMENT, " "), "\n")

            # loop through the list of stocks to present
            for stock in self.stocks_list:
                percent_change = float(stock["percent_change"])
                # slice the time from date/time stamp
                t = dt.datetime.strptime(self.as_of[11:16], "%H:%M")
                as_of = f"a/o {dt.datetime.strftime(t, '%I:%M %p')}"

                # determine text color depending on percent_change value
                # red: negative value, green: positive value, yellow: no change or zero value
                color_code = "\033[22;31;40m" if percent_change < 0 else (
                    "\033[1;32;40m" if percent_change > 0 else "\033[22;33;40m")

                print(
                    f"{color_code}{stock['symbol'].strip().upper().center(SPACE_ALIGNMENT, ' ')}")
                amount = '{:,.2f}'.format(float(stock['price']['amount']))
                change = f" ({'{:+.2f}'.format(percent_change)})"
                amount_and_change = amount + \
                    (change if change != " (+0.00)" else "")
                print(
                    f"{color_code}{amount_and_change.center(SPACE_ALIGNMENT, ' ')}")
                print(
                    f"{color_code}{str('{:,}'.format(int(stock['volume']))).center(SPACE_ALIGNMENT, ' ')}")

                print(
                    f"{color_code}{as_of.center(SPACE_ALIGNMENT, ' ')}\n")

                time.sleep(1)
                tick_count += 1

                if tick_count >= TIME_TO_CHECK_NEW_DATA:
                    # fetch new data from api
                    self.fetch_stocks_json()
                    tick_count = 0
