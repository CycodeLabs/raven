from pathlib import Path
from src.config.config import LAST_QUERY_ID, QUERIES_PATH_DEFAULT

query_dir = Path(__file__).parent.parent.parent / QUERIES_PATH_DEFAULT


def test_report():
    assert query_dir.exists(), f"Directory {query_dir} doesn't exist"
    query_files = list(query_dir.glob("query*.yml"))
    assert (
        len(query_files) > 0
    ), f"Directory {query_dir} doesn't contain any query*.yml files"

    # get query ids from files in query_dir
    query_ids = []
    for query_file in query_files:
        with open(query_file, "r") as f:
            query_id = ""
            while not query_id:  # possible that first line is empty
                line = f.readline()
                if line.startswith("id: RQ-"):
                    query_id = line[4:].strip()
            query_ids.append(query_id)

    max_id_num = max([int(query_id[3:]) for query_id in query_ids])

    # sequence
    assert set(query_ids) == set(
        [f"RQ-{num}" for num in range(1, max_id_num + 1)]
    ), f"Query ids in {query_dir} are not continuous from 1 to {max_id_num}: {query_ids}"

    # last id in files == config.LAST_QUERY_ID
    assert (
        LAST_QUERY_ID == max_id_num
    ), f"LAST_QUERY_ID in config ({LAST_QUERY_ID}) != max id in query files ({max_id_num})"
