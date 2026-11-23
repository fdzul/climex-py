import pandas as pd


def load_centroid_data(path: str, state: str) -> pd.DataFrame:
    """Read a CSV of centroids and keep the rows of one state.

    Parameters
    ----------
    path : str
        CSV with a ``CVEGEO`` column.
    state : str
        Last three characters of ``CVEGEO`` that identify the rows to keep.
    """
    df = pd.read_csv(path, dtype={"CVEGEO": str})
    return df[df["CVEGEO"].str[-3:] == state].reset_index(drop=True)
