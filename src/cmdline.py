import argparse

import src.logger.log as log
from src.downloader.downloader import (
    download_all_workflows_and_actions,
    download_org_workflows_and_actions,
)
from src.indexer.index import index_downloaded_workflows_and_actions
from src.reporter.report import generate
from src.config.config import (
    load_downloader_config,
    load_indexer_config,
    load_reporter_config,
)
from src.config.config import (
    DEBUG_DEFAULT,
    MIN_STARS_DEFAULT,
    NEO4J_CLEAN_DEFAULT,
    NEO4J_URI_DEFAULT,
    NEO4J_USERNAME_DEFAULT,
    NEO4J_PASSWORD_DEFAULT,
    REDIS_HOST_DEFAULT,
    REDIS_PORT_DEFAULT,
    REDIS_CLEAN_DEFAULT,
    REPORT_SLACK_DEFAULT,
)


def execute() -> None:
    try:
        raven()
        log.catch_exit()
    except KeyboardInterrupt:
        log.catch_exit()
    except Exception as e:
        log.error(e)
        log.fail_exit()


def raven() -> None:
    parser = argparse.ArgumentParser(
        description="Github Actions downloader and indexer"
    )

    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    redis_parser = argparse.ArgumentParser(add_help=False)

    # Add redis arguments
    redis_parser.add_argument(
        "--redis-host",
        help=f"Redis host, default {REDIS_HOST_DEFAULT}",
        default=REDIS_HOST_DEFAULT,
    )
    redis_parser.add_argument(
        "--redis-port",
        help=f"Redis port, default {REDIS_CLEAN_DEFAULT}",
        default=REDIS_PORT_DEFAULT,
    )
    redis_parser.add_argument(
        "--clean-redis",
        "-cr",
        action="store_const",
        default=REDIS_CLEAN_DEFAULT,
        const=True,
        help="Whether to clean cache in the redis",
    )

    neo4j_parser = argparse.ArgumentParser(add_help=False)
    neo4j_parser.add_argument(
        "--neo4j-uri",
        default=NEO4J_URI_DEFAULT,
        help=f"Neo4j URI endpoint, default: {NEO4J_URI_DEFAULT}",
    )
    neo4j_parser.add_argument(
        "--neo4j-user",
        default=NEO4J_USERNAME_DEFAULT,
        help=f"Neo4j username, default: {NEO4J_USERNAME_DEFAULT}",
    )
    neo4j_parser.add_argument(
        "--neo4j-pass",
        default=NEO4J_PASSWORD_DEFAULT,
        help=f"Neo4j password, default: {NEO4J_PASSWORD_DEFAULT}",
    )
    neo4j_parser.add_argument(
        "--clean-neo4j",
        "-cn",
        action="store_const",
        default=NEO4J_CLEAN_DEFAULT,
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
        default=DEBUG_DEFAULT,
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
        "--min-stars",
        default=MIN_STARS_DEFAULT,
        help="Minimum number of stars for a repository",
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
        default=DEBUG_DEFAULT,
        const=True,
        help="Whether to print debug statements",
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
        default=REPORT_SLACK_DEFAULT,
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

    args = parser.parse_args()

    command_functions = {
        "download": {
            "crawl": download_all_workflows_and_actions,
            "org": download_org_workflows_and_actions,
        },
        "index": index_downloaded_workflows_and_actions,
        "report": generate,
    }

    if args.command in command_functions:
        if args.command == "download":
            if args.download_command:
                load_downloader_config(vars(args))
                command_functions[args.command][args.download_command]()
                return
            else:
                download_parser.print_help()
        elif args.command == "index":
            load_indexer_config(vars(args))
            command_functions[args.command]()
        elif args.command == "report":
            load_reporter_config(vars(args))
            command_functions[args.command]()
    else:
        parser.print_help()
