import argparse

from downloader import download_all_workflows_and_actions
from indexer import index_downloaded_workflows_and_actions
from config import Config


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Github Actions downloader and indexer"
    )

    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    # Download action
    download_parser = subparsers.add_parser(
        "download", help="Download public Github Actions workflows"
    )
    # TODO: It can be optional eventually.
    download_parser.add_argument(
        "--token",
        required=True,
        help="GITHUB_TOKEN to download data from Github API (Needed for effective rate-limiting)",
    )
    download_parser.add_argument(
        "--output",
        "-o",
        default="data",
        help="Output directory to download the workflows",
    )
    download_parser.add_argument(
        "--max-stars", help="Maximum number of stars for a repository"
    )
    download_parser.add_argument(
        "--min-stars", default=1000, help="Minimum number of stars for a repository"
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

    if not args.command:
        parser.print_help()
        return

    if args.command == "download":
        Config.load_downloader_config(args)
        download_all_workflows_and_actions()
    elif args.command == "index":
        Config.load_indexer_config(args)
        index_downloaded_workflows_and_actions()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
