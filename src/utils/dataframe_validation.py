"""
DataFrame validation utilities to prevent common PySpark errors
"""
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit
from typing import List, Optional, Any


def validate_dataframe(
    df: DataFrame,
    expected_cols: Optional[List[str]] = None,
    df_name: str = "DataFrame"
) -> DataFrame:
    """
    Validate a DataFrame has expected structure
    
    Args:
        df: DataFrame to validate
        expected_cols: List of required column names (optional)
        df_name: Name for error messages
        
    Returns:
        The same DataFrame (for chaining)
        
    Raises:
        ValueError: If validation fails
    """
    if df is None:
        raise ValueError(f"{df_name} is None")
    
    if expected_cols:
        missing_cols = set(expected_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"{df_name} missing columns: {missing_cols}. "
                f"Available: {df.columns}"
            )
    
    # Check for duplicate column names
    if len(df.columns) != len(set(df.columns)):
        duplicates = [c for c in df.columns if df.columns.count(c) > 1]
        raise ValueError(
            f"{df_name} has duplicate columns: {set(duplicates)}"
        )
    
    return df


def assert_no_duplicate_columns(df: DataFrame, df_name: str = "DataFrame"):
    """Check DataFrame has no duplicate column names"""
    if len(df.columns) != len(set(df.columns)):
        duplicates = [c for c in df.columns if df.columns.count(c) > 1]
        raise ValueError(
            f"{df_name} has duplicate columns: {set(duplicates)}\n"
            f"All columns: {df.columns}"
        )


def assert_required_columns(
    df: DataFrame,
    required_cols: List[str],
    df_name: str = "DataFrame"
):
    """Check DataFrame has all required columns"""
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(
            f"{df_name} missing required columns: {missing}\n"
            f"Available: {df.columns}"
        )


def safe_join(
    left_df: DataFrame,
    right_df: DataFrame,
    on_condition: Any,
    select_cols: List[str],
    how: str = "inner"
) -> DataFrame:
    """
    Perform a safe join with explicit column selection
    
    Args:
        left_df: Left DataFrame (will be aliased as 'l')
        right_df: Right DataFrame (will be aliased as 'r')
        on_condition: Join condition using col("l.x") == col("r.y")
        select_cols: List of columns to select (e.g., ["l.id", "l.name", "r.value"])
        how: Join type (default: "inner")
        
    Returns:
        Joined DataFrame with only specified columns
        
    Example:
        result = safe_join(
            members, claims,
            on_condition=col("l.member_id") == col("r.member_id"),
            select_cols=["l.member_id", "l.name", "r.claim_amount"]
        )
    """
    result = left_df.alias("l").join(
        right_df.alias("r"),
        on_condition,
        how
    ).select(*[col(c) for c in select_cols])
    
    assert_no_duplicate_columns(result, "Join result")
    return result


def ensure_schema_for_union(
    df1: DataFrame,
    df2: DataFrame,
    fill_value: Any = None
) -> tuple[DataFrame, DataFrame]:
    """
    Ensure two DataFrames have the same schema for union
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame  
        fill_value: Value to use for missing columns (default: None/null)
        
    Returns:
        Tuple of (df1, df2) with matching schemas
        
    Example:
        df1, df2 = ensure_schema_for_union(df1, df2, fill_value=lit(False))
        result = df1.unionByName(df2)
    """
    cols1 = set(df1.columns)
    cols2 = set(df2.columns)
    
    # Add missing columns to df1
    for col_name in cols2 - cols1:
        df1 = df1.withColumn(col_name, fill_value if fill_value else lit(None))
    
    # Add missing columns to df2
    for col_name in cols1 - cols2:
        df2 = df2.withColumn(col_name, fill_value if fill_value else lit(None))
    
    # Order columns the same way
    all_cols = sorted(set(df1.columns))
    df1 = df1.select(*all_cols)
    df2 = df2.select(*all_cols)
    
    return df1, df2

