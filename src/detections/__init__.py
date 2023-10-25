from src.config.config import Config


class Detection(object):
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

    def filter(self) -> bool:
        return self.filter_queries_by_tags() and self.filter_queries_by_severity()

    def filter_queries_by_severity(self):
        if Config.severity:
            if self.severity in Config.severity:
                return True
            else:
                return False
        else:
            return True

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

    def run(self) -> list:
        """
        Will run the cypher code with the given query.
        and will return the matching workflow paths
        """
        result = Config.graph.run_query(self.query)
        return [dict(record).get("w.path") for record in result]