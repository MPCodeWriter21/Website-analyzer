import sys
import time

import log21

from main import Analyzer, Handler, url_handler

logger = log21.get_logger()


def main():
    # TODO: Well, honestly, I don't like this way of getting inputs! We should do it with an argument parser!
    # Get Website URL
    url = url_check = None
    while not url_check:
        url = logger.input("Please Enter Website URL: ").lower()
        url_check = url_handler(url)
        if not url_check:
            logger.error("Please enter a valid http/https URL")

    # Get Website Name
    name = logger.input("Please Enter Website Name(Optional): ") or "Analyze"

    # You can pass webdriver and saved path as argument to Analyze class

    analyzer = Analyzer(url, name)

    start_time = time.time()

    funcs = [analyzer.get_whois, analyzer.get_responsive, analyzer.get_gtmetrix, analyzer.get_backlinks,
             analyzer.get_amp, analyzer.get_ssl]

    for func in funcs:
        try:
            logger.info("Starting {}".format(func.__name__))
            func()
        except Exception as e:
            logger.error("Error in {}: {}".format(func.__name__, e))
            continue

    # Optimize Images
    while True:
        optimize = logger.input("\nDo you want to optimize images(y/n)? ").lower()
        if optimize == "y":
            analyzer.optimize()
            break
        elif optimize == "n":
            break
        else:
            logger.error("Please enter correct value")

    # Checking running time
    end_time = time.time()
    logger.info(f'Done in {int(end_time - start_time)} seconds.')

    # Close Driver After Analyze
    analyzer.driver.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.clear_line()
        logger.error("KeyboardInterrupt: Exiting...")
        sys.exit(0)
