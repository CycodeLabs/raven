import sys
from typing import Any
from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    colorize=True,
)


def debug(msg: str) -> None:
    from config import Config

    if Config.debug:
        logger.debug(msg)


def error(msg: str) -> None:
    logger.error(msg)


def warning(msg: str) -> None:
    logger.warning(msg)


def catch_exit() -> None:
    from config import Config

    if Config.github_token:
        print("""\n[x] Index results with: python main.py index""")

    elif Config.neo4j_uri:
        neo4j_server = Config.neo4j_uri.split("//")[1].split(":")[0]
        print(f"""\n[x] View results at: http://{neo4j_server}:7474""")

    sys.exit(0)
