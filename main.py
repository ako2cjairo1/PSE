from PSETicker import *


def main():
    try:
        print(f"\n**Fetching stock updates from {URL}")
        pse_ticker.fetch_stocks_json()
        print("\nDone!\n")

        pse_ticker.run_ticker()

    except KeyboardInterrupt:
        print(" OPTION ".center(50, "="))
        print("")
        print(" 1 - Create Watchlist")
        print(" 2 - All Stocks")
        print("")

        option = input("Your input here: ")
        if option.strip() == "1":
            watch_list = input(
                "Input the stock codes here (comma separated): ")
            if watch_list:
                pse_ticker.create_watch_list(watch_list)
                pse_ticker.is_watchlist = True

        elif option.strip() == "2":
            pse_ticker.is_watchlist = False

    main()


if __name__ == "__main__":
    # initialize PSETicker class
    pse_ticker = PSE_Ticker([])
    main()
