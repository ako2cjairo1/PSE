import time
from PSETicker import PSE_Ticker


def user_menu():
    print(" OPTION ".center(50, "="))
    print("")
    print(" a - All Stocks")
    print(" w - Add/Update Watchlist")
    print(" q - Quick Watch")
    print(" c - Create archive")
    print(" s - Sentry Mode\n")
    print(" ** Any Key to Cancel and Continue **\n")

    option = input("Your input here: ").strip().lower()

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


def main():
    url = "https://phisix-api3.appspot.com/"

    try:
        while True:
            print(f"\n**Fetching stock updates from {url}")
            if len(pse_ticker.fetch_stocks_json()) <= 0:
                user_menu()

            pse_ticker.run_ticker()

    except KeyboardInterrupt:
        user_menu()
        main()


if __name__ == "__main__":
    # initialize PSETicker class
    pse_ticker = PSE_Ticker()
    main()

    # pse_ticker.check_api_conn()
