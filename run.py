import sys
import time

import log21

from main import Analyzer, is_valid_url

logger = log21.get_logger()


def main():
    parser = log21.ColorizingArgumentParser()
    parser.add_argument('-u', '--url', help='URL to analyze', required=True)
    parser.add_argument('-o', '--output', help='Output directory name', default='Analyzer')
    parser.add_argument('-d', '--driver', help='ChromeDriver path')
    parser.add_argument('-O', '--optimize', help='Optimize images', action='store_true')
    parser.add_argument('-v', '--verbose', help='Verbose mode', action='store_true')
    parser.add_argument('-q', '--quiet', help='Quiet mode', action='store_true')

    args = parser.parse_args()

    if not is_valid_url(args.url):
        parser.error('Invalid URL')

    if args.verbose and args.quiet:
        parser.error('Cannot use both -v and -q')
    if args.verbose:
        log21.basic_config(level=log21.DEBUG)
    elif args.quiet:
        log21.basic_config(level=log21.ERROR)
        logger.setLevel(log21.ERROR)

    analyzer = Analyzer(args.url, args.output, args.driver, args.verbose)

    start_time = time.time()

    funcs = [
        analyzer.get_whois,
        analyzer.get_responsive,
        analyzer.get_gtmetrix,
        analyzer.get_backlinks,
        analyzer.get_amp,
        analyzer.get_ssl
    ]

    for func in funcs:
        try:
            logger.info(f"Starting {func.__name__}...")
            func()
            logger.info(f"{func.__name__} finished!")
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e.__class__.__name__}: {str(e)}")
            continue

    # Checking running time
    end_time = time.time()
    logger.info(f'Done in {int(end_time - start_time)} seconds.')

    # Optimize Images
    if args.optimize:
        analyzer.optimize()

    # Close Driver After Analyze
    analyzer.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.clear_line()
        logger.error("KeyboardInterrupt: Exiting...")
        sys.exit(0)
