import pandas as pd


def move_column(df, col, pos):
    """ Move a column to a specific index-based location (0-idx).

    :param df: dataframe
    :param col: column to move
    :param pos: Integer. Column index of new position

    :return: dataframe with column moved
    """
    copy = df[col]
    df.drop(labels=[col], axis=1, inplace=True)
    df.insert(int(pos), f"{col}", copy)
    return df

    """
    

    :param df: 
    :param chunk_size: int. Number of records per chunk
    :return: list of DataFrame objects
    """

def split_df(df, chunk_size):
    """
    Split a DataFrame into a list of DataFrames.
    
    Parameters
    ----------
    df : DataFrame to split.
    chunk_size : Number of records per DataFrame

    Returns
    -------
    List of DataFrames
    """
    df.reset_index(inplace=True, drop=True)
    dfs = [df.loc[i:i + chunk_size - 1, :].reset_index(drop=True) for i in range(0, len(df), chunk_size)]
    return dfs


def strip(df):
    """
    Strip leading and trailing spaces for all columns in a DataFrame
    :param df: DataFrame
    :return: DataFrame
    """
    return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)


def strip_mult(df):
    """
    Replace multiple spaces with a single space for all columns in a DataFrame
    :param df: DataFrame
    :return: DataFrame
    """
    return df.apply(lambda x: x.str.replace(r'\s+', ' ') if x.dtype == "object" else x)


def strip_quotes(df):
    """
    Remove all quotation marks from all columns in a DataFrame
    :param df: DataFrame
    :return: DataFrame
    """
    return df.apply(lambda x: x.str.replace('"', '') if x.dtype == "object" else x)

def pct_nan(df):
    """Get the percentage of null records for each column in a DataFrame"""
    return df.isna().mean().round(4) * 100