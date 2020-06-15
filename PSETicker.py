try:
    import os
    import requests
    import json
    import time
    import datetime as dt
    from colorama import init
    import shutil
except Exception:
    print("Some importing libraries are not found.")

URL = "https://phisix-api3.appspot.com/"
SPACE_ALIGNMENT = 20
TIME_TO_CHECK_NEW_DATA = 10
JSON_FILENAME = "stocks.json"
ARCHIVE_FOLDER = "JSON Archive"


class PSE_Ticker:
    def __init__(self):
        self.stocks_list = []
        self.as_of = ""
        self.watch_list = []
        self.is_watchlist = False

    def get_as_of_date(self):
        return self.as_of[:10] if self.as_of else None

    def create_archive(self, forced: bool = False):
        destination_file_path = None
        json_date = self.get_as_of_date()

        try:
            archive_folder = "{}\\{}".format(os.getcwd(), ARCHIVE_FOLDER)
            date_folder = "{}\\{}".format(archive_folder, json_date)

            # format source file
            source = "{}\\{}".format(os.getcwd(), JSON_FILENAME)

            # format destination file dir
            filename = "\\{}.json".format(self.as_of[:19].replace(":", "-"))
            dest = "{}{}".format(date_folder, filename)

            # check if file already exist in archive folder
            if (not os.path.isfile(dest)) or forced:
                if not os.path.isdir(archive_folder):
                    # create archive folder if not existing
                    os.mkdir(archive_folder)
                if json_date and not os.path.isdir(date_folder):
                    # create a date folder if not existing (using date in "as_of" data)
                    os.mkdir(date_folder)

                # create a copy of file to archive folder
                destination_file_path = shutil.copyfile(source, dest)

        except Exception as e:
            print(e)

        return destination_file_path

    def fetch_stocks_json(self):
        response = None
        response_as_of = None

        try:
            # get json data from api
            response = requests.get(f"{URL}stocks.json")
            if response:
                # save the time stamp of json data we got from get request
                response_as_of = json.loads(response.text)["as_of"]

        except Exception:
            print("\n**Update failed, we'll try again after a moment.\n")

        # if not the same date/time stamp save the new data to json file
        if response_as_of and self.as_of != response_as_of:
            self.as_of = response_as_of

            # write the response data to a file (JSON format)
            with open(JSON_FILENAME, "w") as file_write:
                file_write.write(response.text)

            # create archive of json data as file
            self.create_archive()

        if os.path.isfile(JSON_FILENAME):
            # read the created json file
            with open(JSON_FILENAME, "r") as file_read:
                data = json.load(file_read)

                if self.is_watchlist:
                    # append only stocks that are on the watch_list
                    self.stocks_list = [stock for stock in data["stock"]
                                        if stock["symbol"].strip().upper() in self.watch_list]
                else:
                    # append ALL stocks data to stocks_list
                    self.stocks_list = [stock for stock in data["stock"]]

            if len(self.stocks_list) < 1:
                print("\n**No list of stock codes to show\n")

        return self.stocks_list

    def create_watch_list(self, code_csv):
        if code_csv:
            new_list = code_csv.upper().replace(" ", "")  # remove in-between spaces

            temp_list = ""
            if os.path.isfile("watchlist.tmp"):
                with open("watchlist.tmp", "r") as fr:
                    temp_list = fr.read().strip().upper().replace(
                        " ", "")  # remove in-between spaces

            with open("watchlist.tmp", "w") as fw:
                if len(temp_list) > 0:
                    code_csv = "{},{}".format(temp_list, new_list)
                    print(code_csv)
                fw.write(code_csv)

            self.watch_list = code_csv.split(",")
            print(self.watch_list)
            time.sleep(5)
        return self.watch_list

    def create_stock_banner(self, stock: dict):
        percent_change = float(stock["percent_change"])

        # determine text color depending on percent_change value
        # red: negative value, green: positive value, yellow: no change or zero value
        normal_color_code = "\033[22;31;40m" if percent_change < 0 else (
            "\033[1;32;40m" if percent_change > 0 else "\033[22;33;40m")
        price_color_code = "\033[22;37;41m" if percent_change < 0 else (
            "\033[22;30;42m" if percent_change > 0 else "\033[22;30;43m")
        color_reset = "\033[0;39;49m"

        code = stock['symbol'].strip().upper()
        stock_price = stock['price']['amount']
        price = f"{price_color_code} {'{:,.2f}'.format(stock_price)} {color_reset}"
        volume = '{:,}'.format(int(stock['volume']))

        points_change = '{:+.2f}'.format(percent_change / 100)
        percent_change = "{}({}%)".format(
            normal_color_code, percent_change)

        # slice the time from date/time stamp and convert to datetime type
        as_of_date_format = dt.datetime.strptime(
            self.as_of[11:16], "%H:%M")
        # create as desired string time format
        as_of = f"a/o {dt.datetime.strftime(as_of_date_format, '%I:%M %p')}"

        print(code.center(SPACE_ALIGNMENT, ' '))
        print(" " * ((SPACE_ALIGNMENT - (len(price) - 21)) // 2) + price)
        print("{} {}".format(percent_change, points_change).center(
            SPACE_ALIGNMENT + 10, ' '))
        print(volume.center(SPACE_ALIGNMENT, ' '))
        print(as_of.center(SPACE_ALIGNMENT, ' '), "\n")

    def run_ticker(self):
        tick_count = 0
        # initialize text coloring
        init(autoreset=True)

        # clear the console screen
        os.system("cls")
        print("\n")
        while True:
            if self.is_watchlist:
                print("*** WATCHLIST MODE ***".center(SPACE_ALIGNMENT, " "), "\n")

            # loop through the list of stocks to present
            for stock in self.stocks_list:
                self.create_stock_banner(stock)

                time.sleep(1)
                tick_count += 1

                if tick_count >= TIME_TO_CHECK_NEW_DATA:
                    # fetch new data from api
                    self.fetch_stocks_json()
                    tick_count = 0

    def check_api_conn(self):
        try:
            # get json data from api
            response = requests.get(f"{URL}stocks.json")
            print(response.status_code)
            print(response.reason)

        except Exception:
            print("\n**Update failed, we'll try again after a moment.\n")
