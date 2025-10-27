"""
Helper functions for Unity Catalog table operations
"""
from pyspark.sql import SparkSession, DataFrame
from typing import Optional


def create_catalog_if_not_exists(spark: SparkSession, catalog: str):
    """Create catalog if it doesn't exist"""
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog}")
    print(f"✅ Catalog '{catalog}' ready")


def create_schema_if_not_exists(spark: SparkSession, catalog: str, schema: str):
    """Create schema if it doesn't exist"""
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
    print(f"✅ Schema '{catalog}.{schema}' ready")


def create_volume_if_not_exists(
    spark: SparkSession,
    catalog: str,
    schema: str,
    volume: str
):
    """Create volume if it doesn't exist"""
    spark.sql(
        f"CREATE VOLUME IF NOT EXISTS {catalog}.{schema}.{volume}"
    )
    print(f"✅ Volume '{catalog}.{schema}.{volume}' ready")


def write_table(
    df: DataFrame,
    catalog: str,
    schema: str,
    table: str,
    mode: str = "overwrite",
    partition_by: Optional[list] = None
):
    """
    Write DataFrame to Unity Catalog table
    
    Args:
        df: DataFrame to write
        catalog: Catalog name
        schema: Schema name
        table: Table name
        mode: Write mode (default: "overwrite")
        partition_by: List of columns to partition by (optional)
    """
    full_table_name = f"{catalog}.{schema}.{table}"
    
    writer = df.write.format("delta").mode(mode)
    
    if partition_by:
        writer = writer.partitionBy(*partition_by)
    
    writer.saveAsTable(full_table_name)
    
    count = df.count()
    print(f"✅ Written {count:,} rows to {full_table_name}")


def verify_table(spark: SparkSession, catalog: str, schema: str, table: str) -> int:
    """
    Verify table exists and return row count
    
    Returns:
        Row count
    """
    full_table_name = f"{catalog}.{schema}.{table}"
    count = spark.table(full_table_name).count()
    print(f"✅ Verified {full_table_name}: {count:,} rows")
    return count

