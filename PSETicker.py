try:
    import os
    import requests
    import json
    import time
    from datetime import datetime as dt
    from colorama import init
    import shutil
except Exception:
    print("Some importing libraries are not found.")

SPACE_ALIGNMENT = 20
TIME_TO_CHECK_NEW_DATA = 10
JSON_FILENAME = "stocks.json"
ARCHIVE_FOLDER = "JSON Archive"


class PSE_Ticker:
    def __init__(self):
        self.URL = "https://phisix-api3.appspot.com/"
        self.stocks_list = []
        self.ticker_stocks_list = []
        self.as_of = ""
        self.watch_list = []
        self.is_watchlist = False
        self.is_quick_watch = False
        self.is_sentry_mode = False
        self.close_ticker = False

    def get_as_of(self, date_time):
        date_time = date_time.strip().lower()
        if date_time == "date":
            return self.as_of[:10] if self.as_of else None

        elif date_time == "time":
            # slice the time from date/time stamp and convert to datetime type
            as_of_date_format = dt.strptime(
                self.as_of[11:16], "%H:%M")
            # create as desired string time format
            return dt.strftime(as_of_date_format, '%I:%M %p')

    def create_archive(self, forced: bool = False):
        destination_file_path = None
        json_date = self.get_as_of("date")

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
            response = requests.get(f"{self.URL}stocks.json")
            if response:
                # save the time stamp of json data we got from get request
                response_as_of = json.loads(response.text)["as_of"]

        except Exception:
            print("\n**Update failed, we'll try again after a moment.\n")

        # if date/time stamp does not match it means we have a new data from API,
        #  save the new data to json file
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
                    self.stocks_list = [stock for stock in data["stock"]]

        if self.is_watchlist or self.is_quick_watch:
            # replace ticker_stock_list using symbols on watch_list
            self.ticker_stocks_list = [
                stock for stock in self.stocks_list if stock["symbol"].strip().upper() in self.watch_list]
        else:
            # set the ticker list to all stocks list
            self.ticker_stocks_list = self.stocks_list

        if len(self.stocks_list) < 1:
            print("\n**No list of stock codes to show\n")

        time.sleep(3)
        return self.stocks_list

    def create_watch_list(self, code_csv: str, is_quick_watch: bool = False):
        temp_list = ""

        if is_quick_watch and len(code_csv.strip()) == 0:
            # return immediately if no stock code(s) was given and,
            # if quick watch mode, we don't want to alter contents of temp file.
            return self.watch_list

        if len(code_csv.strip()) > 0:
            code_csv = code_csv.upper().replace(" ", "")  # remove in-between spaces
            if is_quick_watch:
                self.is_quick_watch = True
                self.watch_list = code_csv.split(",")
                # return immediately, no need to write it on temp file
                return self.watch_list

        if os.path.isfile("watchlist.tmp") and not is_quick_watch:
            with open("watchlist.tmp", "r") as fr:
                temp_list = fr.read().strip().upper().replace(
                    " ", "")  # remove in-between spaces

        with open("watchlist.tmp", "w") as fw:
            if temp_list and code_csv:
                # append user inputed code(s) to temp_list
                temp_list = "{},{}".format(temp_list, code_csv)
            elif code_csv:
                temp_list = code_csv

            # proceed if there is something to write
            if temp_list:
                fw.write(temp_list)
                self.is_watchlist = True

        self.watch_list = temp_list.split(",")
        return self.watch_list

    def create_stock_banner(self, stock):
        percent_change = float(stock["percent_change"])

        # determine text color depending on percent_change value
        # red: negative value, green: positive value, yellow: no change or zero value
        normal_color_code = "\033[22;31;40m" if percent_change < 0 else (
            "\033[1;32;40m" if percent_change > 0 else "\033[22;33;40m")
        price_color_code = "\033[22;37;41m" if percent_change < 0 else (
            "\033[22;30;42m" if percent_change > 0 else "\033[22;30;43m")
        color_reset = "\033[0;39;49m"

        code = stock["symbol"].strip().upper()
        stock_price = stock["price"]["amount"]
        price = f"{price_color_code} {'{:,.2f}'.format(stock_price)} {color_reset}"
        volume = "{:,}".format(int(stock["volume"]))

        points_change = "{:+.2f}".format(stock_price * (percent_change / 100))
        percent_change = "{}({:+.2f}%)".format(normal_color_code,
                                               percent_change)

        # create as desired string time format
        as_of = f"a/o {self.get_as_of('time')}"

        print(code.center(SPACE_ALIGNMENT, " "))
        print(" " * ((SPACE_ALIGNMENT - (len(price) - 21)) // 2) + price)
        print("{} {}".format(percent_change, points_change).center(
            SPACE_ALIGNMENT + 10, " "))
        print(volume.center(SPACE_ALIGNMENT, " "))
        print("{}".format(stock["name"]).center(SPACE_ALIGNMENT, " "), "\n")
        # print(as_of.center(SPACE_ALIGNMENT, ' '), "\n")

    def run_ticker(self):
        tick_count = 0

        if len(self.ticker_stocks_list) < 1:
            # return immediately if no list of stocks to show
            print("\n**No list of stock codes to show\n")
            return

        # clear the console screen
        os.system("cls")
        # initialize text coloring
        init(autoreset=True)
        print("\n")

        while True:
            if self.close_ticker:
                return
            if self.is_quick_watch:
                print("*** QUICK WATCH ***".center(SPACE_ALIGNMENT, " "), "\n")
            elif self.is_watchlist:
                print("*** WATCHLIST MODE ***".center(SPACE_ALIGNMENT, " "), "\n")

            # loop through the list of stocks to present
            for stock in self.ticker_stocks_list:
                self.create_stock_banner(stock)

                time.sleep(1)
                tick_count += 1

                if tick_count >= TIME_TO_CHECK_NEW_DATA:
                    # attempt to fetch new data from api
                    self.fetch_stocks_json()
                    tick_count = 0
                    print("\n*** as of {} ***\n".format(self.get_as_of("time")))

    def check_api_conn(self):
        try:
            # get json data from api
            response = requests.get(f"{self.URL}stocks.json")
            print(response.status_code)
            print(response.reason)

        except Exception:
            print("\n**Update failed, we'll try again after a moment.\n")

    def sentry_mode(self):
        response = None
        response_as_of = None
        self.is_sentry_mode = True

        while self.is_sentry_mode:
            print("\n*** SENTRY MODE ***")
            print("waiting for the API to go on-line...\n")

            try:
                # get json data from api
                response = requests.get(f"{self.URL}stocks.json")
                if response:
                    # save the time stamp of json data we got from get request
                    response_as_of = json.loads(response.text)["as_of"]

            except Exception:
                print("\n**Update failed, we'll try again after a moment.\n")

            # if we got date/time stamp it means we have a new data from API,
            if response_as_of:
                # turn off Sentry mode
                self.is_sentry_mode = False
                return

            time.sleep(5)
