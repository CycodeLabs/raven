import os
from typing import List


class Cache:
    """Simple caching/history mechanism which has a file that backs it up.
    Could be improved to Redis for better performance.
    Used not to download/index files twice.

    Every couple of insertions, backing the data to the file.
    """

    def __init__(
        self,
        fpath: str = None,
        num_insertions_to_backup: int = 10,
        clean_cache: bool = False,
    ):
        """The cache can have a file which backup it,
        or without one (only in memory)
        """
        self.fpath = fpath
        self.cache = []
        self.cache_to_backup = []
        self.num_insertions_to_backup = num_insertions_to_backup

        if self.fpath and clean_cache:
            os.remove(self.fpath)
            with open(fpath, "w") as f:
                pass

        for entry in self._get_entries_from_file():
            self.cache.append(entry)

    def insert_to_cache(self, entry: str) -> None:
        if not self.exists_in_cache(entry):
            self.cache.append(entry)
            self.cache_to_backup.append(entry)

            if len(self.cache_to_backup) >= self.num_insertions_to_backup:
                for cached_entry in self.cache_to_backup:
                    self._add_entry_to_file(cached_entry)
                self.cache_to_backup = []

    def exists_in_cache(self, entry: str) -> bool:
        return entry in self.cache

    def _get_entries_from_file(self) -> List[str]:
        if self.fpath:
            with open(self.fpath, "r") as f:
                lines = f.readlines()

            return [line.strip() for line in lines]
        else:
            return []

    def _add_entry_to_file(self, entry: str) -> None:
        if self.fpath:
            with open(self.fpath, "a") as f:
                f.write(entry)
                f.write("\n")
