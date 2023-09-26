import argparse

from downloader import (
    download_all_workflows_and_actions,
    download_org_workflows_and_actions,
)
from indexer import index_downloaded_workflows_and_actions
from reporter.report import generate
from tests.test_raven import test
from config import Config
import logger


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Github Actions downloader and indexer"
    )

    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    redis_parser = argparse.ArgumentParser(add_help=False)

    # Add redis arguments
    redis_parser.add_argument(
        "--redis-host", help="Redis host, default localhost", default="localhost"
    )
    redis_parser.add_argument(
        "--redis-port", help="Redis port, default 6379", default=6379
    )
    redis_parser.add_argument(
        "--clean-redis",
        "-cr",
        action="store_const",
        default=False,
        const=True,
        help="Whether to clean cache in the redis",
    )

    neo4j_parser = argparse.ArgumentParser(add_help=False)
    neo4j_parser.add_argument(
        "--neo4j-uri",
        default="neo4j://localhost:7687",
        help="Neo4j URI endpoint, default: neo4j://localhost:7687",
    )
    neo4j_parser.add_argument(
        "--neo4j-user",
        default="neo4j",
        help="Neo4j username, default: neo4j",
    )
    neo4j_parser.add_argument(
        "--neo4j-pass",
        default="123456789",
        help="Neo4j password, default: 123456789",
    )
    neo4j_parser.add_argument(
        "--clean-neo4j",
        action="store_const",
        default=False,
        const=True,
        help="Whether to clean cache, and index from scratch",
    )

    download_parser_options = argparse.ArgumentParser(add_help=False)
    download_parser_options.add_argument(
        "--token",
        required=True,
        help="GITHUB_TOKEN to download data from Github API (Needed for effective rate-limiting)",
    )
    download_parser_options.add_argument(
        "--debug",
        action="store_const",
        default=False,
        const=True,
        help="Whether to print debug statements",
    )

    download_parser = subparsers.add_parser(
        "download", help="Download workflows into Redis database"
    )

    download_sub_parser = download_parser.add_subparsers(
        dest="download_command",
    )

    crawl_download_parser = download_sub_parser.add_parser(
        "crawl",
        help="Crawl Public GitHub repositories",
        parents=[download_parser_options, redis_parser],
    )

    org_download_parser = download_sub_parser.add_parser(
        "org",
        help="Scan specific GitHub organization",
        parents=[download_parser_options, redis_parser],
    )

    crawl_download_parser.add_argument(
        "--max-stars", help="Maximum number of stars for a repository"
    )
    crawl_download_parser.add_argument(
        "--min-stars", default=1000, help="Minimum number of stars for a repository"
    )

    org_download_parser.add_argument(
        "--org-name",
        required=True,
        help="Organization name to download the workflows",
    )

    # Index action
    index_parser = subparsers.add_parser(
        "index",
        parents=[redis_parser, neo4j_parser],
        help="Index the download workflows into Neo4j database",
    )
    index_parser.add_argument(
        "--debug",
        action="store_const",
        default=False,
        const=True,
        help="Whether to print debug statements",
    )
    index_parser.add_argument(
        "--threads", "-t", type=int, default=1, help="Number of threads, default: 1"
    )

    report_parser = subparsers.add_parser(
        "report",
        parents=[redis_parser, neo4j_parser],
        help="Generate report from indexed Actions",
    )
    report_parser.add_argument(
        "--slack",
        "-s",
        action="store_const",
        default=False,
        const=True,
        help="Send report to slack channel",
    )
    report_parser.add_argument(
        "--slack-token",
        "-st",
        default="",
        help="Send report to slack channel",
    )
    report_parser.add_argument(
        "--channel-id",
        "-ci",
        default="",
        help="Send report to slack channel",
    )

    test_parser = subparsers.add_parser(
        "test",
        parents=[redis_parser, neo4j_parser],
        help="Test RAVEN (for development purposes only)",
    )

    args = parser.parse_args()

    command_functions = {
        "download": {
            "crawl": download_all_workflows_and_actions,
            "org": download_org_workflows_and_actions,
        },
        "index": index_downloaded_workflows_and_actions,
        "report": generate,
        "test": test,
    }

    if args.command in command_functions:
        if args.command == "download":
            if args.download_command:
                Config.load_downloader_config(vars(args))
                command_functions[args.command][args.download_command]()
                return
            else:
                download_parser.print_help()
        elif args.command == "index":
            Config.load_indexer_config(vars(args))
        elif args.command == "report":
            Config.load_reporter_config(vars(args))
        elif args.command == "test":
            Config.load_indexer_config(vars(args))

        command_functions[args.command]()
        return
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
        logger.catch_exit()
    except KeyboardInterrupt:
        logger.catch_exit()
    except Exception as e:
        if isinstance(e, AssertionError):
            logger.error("[x] Some tests are failing")
        else:
            logger.error(e)

        logger.fail_exit()
