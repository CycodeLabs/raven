import argparse
import src.logger.log as log
from src.common.utils import validate_query_ids
from src.downloader.download import (
    download_all_workflows_and_actions,
    download_account_workflows_and_actions,
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
    DOWNLOAD_COMMAND,
    DOWNLOAD_ACCOUNT_COMMAND,
    DOWNLOAD_CRAWL_COMMAND,
    INDEX_COMMAND,
    REPORT_COMMAND,
    QUERIES_PATH_DEFAULT,
    REPORT_RAW_FORMAT,
    REPORT_JSON_FORMAT,
    SEVERITY_LEVELS,
    QUERY_TAGS,
    QUERY_IDS,
)

COMMAND_FUNCTIONS = {
    DOWNLOAD_COMMAND: {
        DOWNLOAD_CRAWL_COMMAND: download_all_workflows_and_actions,
        DOWNLOAD_ACCOUNT_COMMAND: download_account_workflows_and_actions,
    },
    INDEX_COMMAND: index_downloaded_workflows_and_actions,
    REPORT_COMMAND: generate,
}


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
        help=f"Redis host, default: {REDIS_HOST_DEFAULT}",
        default=REDIS_HOST_DEFAULT,
    )
    redis_parser.add_argument(
        "--redis-port",
        type=int,
        help=f"Redis port, default: {REDIS_PORT_DEFAULT}",
        default=REDIS_PORT_DEFAULT,
    )
    redis_parser.add_argument(
        "--clean-redis",
        "-cr",
        action="store_const",
        default=REDIS_CLEAN_DEFAULT,
        const=True,
        help=f"Whether to clean cache in the redis, default: {REDIS_CLEAN_DEFAULT}",
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
        help=f"Whether to clean cache, and index from scratch, default: {NEO4J_CLEAN_DEFAULT}",
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
        help=f"Whether to print debug statements, default: {DEBUG_DEFAULT}",
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

    account_download_parser = download_sub_parser.add_parser(
        "account",
        help="Scan a specific GitHub account (user or organization)",
        parents=[download_parser_options, redis_parser],
    )

    crawl_download_parser.add_argument(
        "--max-stars", type=int, help="Maximum number of stars for a repository"
    )
    crawl_download_parser.add_argument(
        "--min-stars",
        type=int,
        default=MIN_STARS_DEFAULT,
        help=f"Minimum number of stars for a repository, default: {MIN_STARS_DEFAULT}",
    )

    account_download_parser.add_argument(
        "--account-name",
        required=True,
        action="append",
        type=str,
        help="Account name for downloading the workflows",
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
        help=f"Whether to print debug statements, default: {DEBUG_DEFAULT}",
    )

    report_parser = subparsers.add_parser(
        "report",
        parents=[redis_parser, neo4j_parser],
        help="Generate report from indexed Actions - Beta Version",
    )

    report_parser.add_argument(
        "--tag",
        "-t",
        action="append",
        type=str,
        default=[],
        choices=QUERY_TAGS,
        help="Filter queries with specific tag",
    )
    report_parser.add_argument(
        "--severity",
        "-s",
        type=str,
        default="info",
        choices=SEVERITY_LEVELS.keys(),
        help="Filter queries by severity level (default: info)",
    )
    report_parser.add_argument(
        "--query_ids",
        "-id",
        type=validate_query_ids,
        default="",
        metavar=f"RQ-1,..,{QUERY_IDS[-1]}",
        help="Filter queries by query ids (example: RQ-2,RQ-8)",
    )
    report_parser.add_argument(
        "--queries-path",
        "-dp",
        default=QUERIES_PATH_DEFAULT,
        help="Queries folder (default: library)",
    )
    report_parser.add_argument(
        "--format",
        "-f",
        default=REPORT_RAW_FORMAT,
        choices=[REPORT_RAW_FORMAT, REPORT_JSON_FORMAT],
        help="Report format (default: raw)",
    )

    format_sub_parser = report_parser.add_subparsers(
        dest="report_command",
    )

    slack_parser = format_sub_parser.add_parser(
        "slack",
        help="Send report to slack channel",
    )
    slack_parser.add_argument(
        "--slack-token",
        "-st",
        required=True,
        help="Send report to slack channel",
    )
    slack_parser.add_argument(
        "--channel-id",
        "-ci",
        required=True,
        help="Send report to slack channel",
    )

    args = parser.parse_args()

    if args.command in COMMAND_FUNCTIONS:
        if args.command == DOWNLOAD_COMMAND:
            if args.download_command:
                load_downloader_config(vars(args))
                COMMAND_FUNCTIONS[args.command][args.download_command]()
                return
            else:
                download_parser.print_help()
        elif args.command == INDEX_COMMAND:
            load_indexer_config(vars(args))
            COMMAND_FUNCTIONS[args.command]()
        elif args.command == REPORT_COMMAND:
            load_reporter_config(vars(args))
            COMMAND_FUNCTIONS[args.command]()
    else:
        parser.print_help()
