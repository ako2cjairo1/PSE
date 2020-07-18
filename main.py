import time
from datetime import datetime as dt
from PSENews import PSE_News
from PSETicker import PSE_Ticker
from threading import Thread



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
    pse_ticker.close_ticker = False

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
    # create a temporary watchlist
    elif option == "q":
        quick_watch_list = input(
            "Input the stock codes here (comma separated): ")
        pse_ticker.create_watch_list(quick_watch_list, is_quick_watch=True)
    elif option == "s":
        pse_ticker.sentry_mode()
        main()
    elif option == "n":
        try:
            pse_news.show_news_banner()
        except KeyboardInterrupt:
            user_menu()
            main()
    elif option == "x":
        exit()


def main():
    url = "https://phisix-api3.appspot.com/"

    def run_PSE_News():
        time_ticker = 0
        while True:
            t = dt.now()
            hr = t.hour
            mn = t.minute
            sc = t.second

            if time_ticker == 0 and (hr == 12 and mn == 55 and sc == 0):
                pse_ticker.close_ticker = True
                time_ticker += 1

            if time_ticker >= 1:
                time_ticker = 0

            time.sleep(1)

    pseNews_thread = Thread(target=run_PSE_News)
    pseNews_thread.start()

    try:
        while True:
            print(f"\n**Fetching stock updates from {pse_ticker.URL}")
            if len(pse_ticker.fetch_stocks_json()) <= 0:
                pse_ticker.sentry_mode()
                continue

            if pse_ticker.close_ticker:
                pse_news.show_news_banner()
            else:
                pse_ticker.run_ticker()

    except KeyboardInterrupt:
        user_menu()
        main()


if __name__ == "__main__":
    # init PSETicker class
    pse_ticker = PSE_Ticker()

    # init PSE_News class
    pse_news = PSE_News()

    # proceed to user options
    main()
    # pse_ticker.check_api_conn()
