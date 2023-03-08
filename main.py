import time
import os
import sys
from datetime import datetime as dt
from PSENews import PSE_News
from PSETicker import PSE_Ticker
from threading import Event, Thread

pse_news_event = Event()


def user_menu():
    print(" OPTION ".center(50, "="))
    print("")
    print(" a - All Stocks")
    print(" w - Add/Update Watchlist")
    print(" q - Quick Watch")
    print(" n - PH Business News")
    print(" c - Create archive")
    print(" s - Sentry Mode\n")
    print(" x - Close\n")
    print(" ** Any Key to Cancel and Continue **\n")

    option = input("Your input here: ").strip().lower()
    pse_ticker.hide_ticker = False
    pse_news_event.set()

    # create a watchlist of stocks
    if option == "w":
        watch_list = input(
            "Input the stock codes here (comma separated): ")
        pse_ticker.create_watch_list(watch_list)
    # show banner of all stocks
    elif option == "a":
        pse_ticker.is_watchlist = False
        pse_ticker.is_quick_watch = False
    # create archive of json file
    elif option == "c":
        archive = pse_ticker.create_archive(forced=True)
        if archive:
            print("\nArchive created: ", archive)
            time.sleep(2)
    # create a temporary watch list
    elif option == "q":
        quick_watch_list = input(
            "Input the stock codes here (comma separated): ")
        pse_ticker.create_watch_list(quick_watch_list, is_quick_watch=True)
    elif option == "s":
        pse_ticker.sentry_mode()
        main()
    elif option == "n":
        # pse_news.hide_ticker = True
        pse_news.banner_thread = Event()
        pse_news.show_news_banner()
        main()
    elif option == "x":
        exit()


def main():
    url = "https://phisix-api3.appspot.com/"

    def run_PSE_News():
        time_ticker = 0
        while not pse_news_event.is_set():
            t = dt.now()
            day = t.isoweekday()
            hr = t.hour
            mn = t.minute
            sc = t.second
            isCheck = True if (
                time_ticker == 0 and day in range(1, 6)) else False

            if isCheck and (hr <= 9 and mn <= 20 and sc == 0):
                # Pre-open / Open Market
                pse_ticker.is_sentry_mode = True
                pse_ticker.hide_ticker = False
                time_ticker += 1
                pse_ticker.status_message = "Pre-open"
            elif isCheck and ((9 >= hr < 12) and mn <= 30 and sc == 0):
                pse_ticker.status_message = f"Market Open"
                time_ticker += 1
            elif isCheck and (hr == 12 and mn <= 59 and sc == 0):
                # Market Recess
                pse_ticker.hide_ticker = True
                pse_ticker.status_message = "Market Recess"
                time_ticker += 1
            elif isCheck and (hr == 13 and mn >= 30 and sc == 0):
                # Resume Market
                pse_ticker.hide_ticker = False
                pse_ticker.status_message = f"Market Open"
                pse_news.banner_thread.set()  # end the news banner daemon thread
                time_ticker += 1
            elif isCheck and (hr == 14 and (55 >= mn >= 50) and sc == 0):
                # Run-off Period
                os.system("say 'Philippine Stock Exchange Run-off period.'")
                pse_ticker.status_message = f"Market Run-off"
                time_ticker += 1
            elif isCheck and (hr == 15 and (mn < 2) and sc == 0):
                # Market Closed
                os.system("say 'Philippine Stock Exchange is now closed.'")
                pse_ticker.status_message = f"Market Close"
                time_ticker += 1
            elif isCheck and (hr == 15 and mn >= 10 and sc == 0):
                os.system("say 'Closing Philippine Stock Exchange ticker.'")
                time.sleep(3)
                pse_news_event.set()
                pse_ticker.close_ticker = True
                os.system("clear")
                exit()

            if time_ticker >= 1:
                time_ticker = 0
            time.sleep(1)
        return exit()

    pse_news_event = Event()
    Thread(target=run_PSE_News, daemon=True).start()

    try:
        while not pse_ticker.close_ticker:
            print(f"\n**Fetching stock updates from {pse_ticker.URL}")
            stock_updates = pse_ticker.fetch_stocks_json()

            if pse_ticker.is_sentry_mode or len(stock_updates) <= 0:
                os.system(
                    f"say 'Philippine Stock Exchange will open shortly, entering sentry mode...'")

                pse_ticker.sentry_mode()
            elif pse_ticker.hide_ticker:
                os.system(
                    "say 'Philippine Stock Exchange is on recess. Now loading business news banner...'")
                pse_news.banner_thread = Event()
                pse_news.show_news_banner()
            elif not pse_ticker.hide_ticker:
                pse_news.banner_thread.set()
                os.system(
                    f"say 'Philippine Stock Exchange is online...{pse_ticker.status_message}'")
                pse_ticker.run_ticker()

            time.sleep(1)

    except KeyboardInterrupt:
        pse_news_event.set()
        user_menu()
        main()


if __name__ == "__main__":
    # init PSETicker class
    pse_ticker = PSE_Ticker()

    # init PSE_News class
    pse_news = PSE_News()

    # this line will invoke the watch list mode
    pse_ticker.create_watch_list("")
    # proceed to user options
    main()
    # pse_ticker.check_api_conn()
