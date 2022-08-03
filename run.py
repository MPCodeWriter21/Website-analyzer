import sys
import time

import log21

from main import Analyzer, url_handler

logger = log21.get_logger()


def main():
    parser = log21.ColorizingArgumentParser()
    parser.add_argument('-u', '--url', help='URL to analyze', required=True)
    parser.add_argument('-o', '--output', help='Output directory name', default='Analyzer')
    parser.add_argument('-d', '--driver', help='ChromeDriver path')
    parser.add_argument('-v', '--verbose', help='Verbose mode', action='store_true')

    args = parser.parse_args()

    if not url_handler(args.url):
        parser.error('Invalid URL')

    analyzer = Analyzer(args.url, args.output, args.driver, args.verbose)

    start_time = time.time()

    funcs = [analyzer.get_whois,
             analyzer.get_responsive,
             # analyzer.get_gtmetrix,
             analyzer.get_backlinks,
             analyzer.get_amp,
             analyzer.get_ssl]

    for func in funcs:
        try:
            logger.info(f"Starting {func.__name__}")
            func()
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e.__class__.__name__}: {str(e)}")
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
