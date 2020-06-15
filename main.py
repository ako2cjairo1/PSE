import time
from PSETicker import PSE_Ticker


def main():
    url = "https://phisix-api3.appspot.com/"
    try:
        print(f"\n**Fetching stock updates from {url}")
        pse_ticker.fetch_stocks_json()
        print("\nDone!\n")

        pse_ticker.run_ticker()

    except KeyboardInterrupt:
        print(" OPTION ".center(50, "="))
        print("")
        print(" 1 - Add/Update Watchlist")
        print(" 2 - All Stocks")
        print(" 3 - Create archive\n")
        print(" ** Any Key to Cancel and Continue **\n")

        option = input("Your input here: ")
        if option.strip() == "1":                                   # create a watchlist of stocks
            watch_list = input(
                "Input the stock codes here (comma separated): ")
            if watch_list:
                pse_ticker.create_watch_list(watch_list)
                pse_ticker.is_watchlist = True
        elif option.strip() == "2":                                 # show banner of all stocks
            pse_ticker.is_watchlist = False

        elif option.strip() == "3":                                 # create archive of json file
            archive = pse_ticker.create_archive(forced=True)
            if archive:
                print("\nArchive created: ", archive)
                time.sleep(2)

    main()


if __name__ == "__main__":
    # initialize PSETicker class
    pse_ticker = PSE_Ticker()
    main()
