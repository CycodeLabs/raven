import argparse

from downloader import download_all_workflows_and_actions, download_org_workflows_and_actions
from indexer import index_downloaded_workflows_and_actions
from config import Config


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Github Actions downloader and indexer"
    )

    subparsers = parser.add_subparsers(dest="command", help="sub-command help")
    download_parser_options = argparse.ArgumentParser(add_help=False)
    download_parser_options.add_argument(
        "--token",
        required=True,
        help="GITHUB_TOKEN to download data from Github API (Needed for effective rate-limiting)",
    )
    download_parser_options.add_argument(
        "--output",
        "-o",
        default="data",
        help="Output directory to download the workflows",
    )

    download_parser = subparsers.add_parser(
        "download", parents=[download_parser_options], help="Download workflows into Redis database"
    )

    download_sub_parser = download_parser.add_subparsers(
        dest="download_command"
    )

    crawl_download_parser = download_sub_parser.add_parser(
        "crawl", help="Crawl Public GitHub repositories"
    )

    org_download_parser = download_sub_parser.add_parser(
        "org", help="Scan specific GitHub organization"
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
        "index", help="Index the download workflows into Neo4j database"
    )
    index_parser.add_argument(
        "--input",
        "-i",
        default="data",
        help="Input directory with the downloaded workflows",
    )
    index_parser.add_argument(
        "--neo4j-uri",
        default="neo4j://localhost:7687",
        help="Neo4j URI endpoint",
    )
    index_parser.add_argument(
        "--neo4j-user",
        default="neo4j",
        help="Neo4j username",
    )
    index_parser.add_argument(
        "--neo4j-pass",
        default="test",
        help="Neo4j password",
    )
    # Currently there are issues in multi-threading
    # (especially regarding composite actions/reusable workflows)
    index_parser.add_argument(
        "--threads", "-t", type=int, default=1, help="Number of threads"
    )
    index_parser.add_argument(
        "--clean",
        "-c",
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
    main()