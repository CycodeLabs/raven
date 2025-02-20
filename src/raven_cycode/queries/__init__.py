from src.config.config import Config, SEVERITY_LEVELS
import json
from colorama import Fore, Style, init
import textwrap

init()


class Query(object):
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        tags: list,
        severity: str,
        query: list,
    ) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.tags = tags
        self.severity = severity
        self.query = query
        self.result = None

    def filter(self) -> bool:
        return (
            self.filter_queries_by_tags()
            and self.filter_queries_by_severity()
            and self.filter_queries_by_query_id()
        )

    def filter_queries_by_severity(self):
        severity_level = SEVERITY_LEVELS.get(Config.severity, 0)
        severity_levels = [
            severity
            for severity, level in SEVERITY_LEVELS.items()
            if level >= severity_level
        ]

        return self.severity in severity_levels

    def filter_queries_by_tags(self):
        if not Config.tags:
            # If no tags has been given, return all detections
            return True

        for tag in self.tags:
            # If this detection tag is matching the
            # supplied tags
            if tag in Config.tags:
                return True

        # If no detections found with the input tags
        # skip this detection
        return False

    def filter_queries_by_query_id(self):
        if not Config.query_ids:
            return True

        if self.id in Config.query_ids:
            return True

        return False

    def run(self) -> list:
        """
        Will run the cypher code with the given query.
        and will return the matching workflow paths
        """
        result = Config.graph.run_query(self.query)
        self.result = [dict(record).get("url") for record in result]

    def to_raw(self) -> str:
        report = ""
        description_length = 80

        report += f"{Fore.CYAN}Name:{Style.RESET_ALL} {self.name}\n"
        report += f"{Fore.CYAN}Severity:{Style.RESET_ALL} {self.severity}\n"

        wrapped_description = textwrap.fill(self.description, width=description_length)
        report += f"{Fore.CYAN}Description:{Style.RESET_ALL} {wrapped_description}\n"
        report += f"{Fore.CYAN}Tags:{Style.RESET_ALL} {self.tags}\n"

        report += f"{Fore.CYAN}Workflow URLS:{Style.RESET_ALL}\n"
        for url in self.result:
            report += f"- {url}\n"

        return report

    def to_json(self) -> str:
        return self._to_dict()

    def _to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "severity": self.severity,
            "result": self.result,
        }
