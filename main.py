import argparse

from downloader import download_all_workflows_and_actions, download_org_workflows_and_actions
from indexer import index_downloaded_workflows_and_actions
from config import Config
import exceptions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Github Actions downloader and indexer"
    )

    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    redis_parser = argparse.ArgumentParser(add_help=False)
    
    # Add redis arguments
    redis_parser.add_argument("--redis-host", help="Redis host, default localhost", default="localhost")
    redis_parser.add_argument("--redis-port", help="Redis port, default 6379", default=6379)
    redis_parser.add_argument(
        "--clean-redis",
        "-cr",
        action="store_const",
        default=False,
        const=True,
        help="Whether to clean cache in the redis",
    )

    download_parser_options = argparse.ArgumentParser(add_help=False)
    download_parser_options.add_argument(
        "--token",
        required=True,
        help="GITHUB_TOKEN to download data from Github API (Needed for effective rate-limiting)",
    )

    download_parser = subparsers.add_parser(
        "download", help="Download workflows into Redis database"
    )

    download_sub_parser = download_parser.add_subparsers(
        dest="download_command",
    )

    crawl_download_parser = download_sub_parser.add_parser(
        "crawl", help="Crawl Public GitHub repositories",
        parents=[download_parser_options, redis_parser]
    )

    org_download_parser = download_sub_parser.add_parser(
        "org", help="Scan specific GitHub organization",
        parents=[download_parser_options, redis_parser]
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
        "index", parents=[redis_parser], help="Index the download workflows into Neo4j database"
    )
    index_parser.add_argument(
        "--neo4j-uri",
        default="neo4j://localhost:7687",
        help="Neo4j URI endpoint, default: neo4j://localhost:7687",
    )
    index_parser.add_argument(
        "--neo4j-user",
        default="neo4j",
        help="Neo4j username, default: neo4j",
    )
    index_parser.add_argument(
        "--neo4j-pass",
        default="123456789",
        help="Neo4j password, default: 123456789",
    )
    # Currently there are issues in multi-threading
    # (especially regarding composite actions/reusable workflows)
    index_parser.add_argument(
        "--threads", "-t", type=int, default=1, help="Number of threads, default: 1"
    )
    index_parser.add_argument(
        "--clean-neo4j",
        "-cn",
        action="store_const",
        default=False,
        const=True,
        help="Whether to clean cache, and index from scratch",
    )

    args = parser.parse_args()

    command_functions = {
        "download": {
            "crawl": download_all_workflows_and_actions,
            "org": download_org_workflows_and_actions,
        },
        "index": index_downloaded_workflows_and_actions,
    }
    
    if args.command in command_functions:
        if args.command == "download":
            if args.download_command:
                Config.load_downloader_config(vars(args))
                command_functions[args.command][args.download_command]()
            else:
                 download_parser.print_help()
        elif args.command == "index":
                Config.load_indexer_config(vars(args))
                command_functions[args.command]()
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
         exceptions.catch_exit()