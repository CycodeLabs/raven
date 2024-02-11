from pathlib import Path
from src.config.config import LAST_QUERY_ID, QUERIES_PATH_DEFAULT
from yaml import safe_load

query_dir = Path(__file__).parent.parent.parent / QUERIES_PATH_DEFAULT

RQ_PREFIX = "RQ-"


def test_report():
    assert query_dir.exists(), f"Directory {query_dir} doesn't exist"
    query_files = list(query_dir.glob("query*.yml"))
    assert (
        len(query_files) > 0
    ), f"Directory {query_dir} doesn't contain any query*.yml files"

    # get query ids from files in query_dir
    query_ids = []
    for query_file in query_files:
        with open(query_file, "r") as query:
            parsed_query = safe_load(query)
            if not parsed_query:
                raise ValueError(f"{query_file} is not a valid query file")

            query_id = parsed_query.get("id")
            try:
                int(query_id.split(RQ_PREFIX)[1])
            except ValueError:
                raise ValueError(f"Query {query_file} has invalid id")

            query_info = parsed_query.get("info")

            assert parsed_query["query"], f"Query in {query_file} is empty"
            assert query_info["name"], f"Query in {query_file} has no name"
            assert query_info["severity"], f"Query in {query_file} has no severity"
            assert query_info[
                "description"
            ], f"Query in {query_file} has no description"
            assert query_info["tags"], f"Query in {query_file} has no tags"

            query_ids.append(parsed_query.get("id"))

    try:
        max_id_num = max([int(query_id.split(RQ_PREFIX)[1]) for query_id in query_ids])
    except ValueError:
        raise ValueError(f"Added query has invalid id")

    # sequence
    assert set(query_ids) == set(
        [f"RQ-{num}" for num in range(1, max_id_num + 1)]
    ), f"Query ids in {query_dir} are not continuous from 1 to {max_id_num}: {query_ids}"

    # last id in files == config.LAST_QUERY_ID
    assert (
        LAST_QUERY_ID == max_id_num
    ), f"LAST_QUERY_ID in config ({LAST_QUERY_ID}) != max id in query files ({max_id_num})"
