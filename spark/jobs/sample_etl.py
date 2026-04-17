#!/usr/bin/env python3
"""
Sample ETL with Nessie - Create and query Iceberg tables using Nessie.
Demonstrates data transformation and table creation on Nessie/Iceberg.
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from datetime import datetime

def main():
    # Initialize Spark session with Nessie catalog
    spark = SparkSession.builder \
        .appName("sample-etl-nessie") \
        .getOrCreate()
    
    print("=" * 80)
    print("Sample ETL with Nessie - Creating and querying Iceberg tables")
    print("=" * 80)
    
    try:
        # Create DataFrame from sample data
        print("\n1️⃣  Creating sample data...")
        data = [
            ("Alice", 25, 60000.0),
            ("Bob", 30, 75000.0),
            ("Charlie", 35, 90000.0),
            ("Diana", 28, 70000.0),
            ("Eve", 32, 85000.0),
        ]
        
        schema = StructType([
            StructField("name", StringType(), True),
            StructField("age", IntegerType(), True),
            StructField("salary", DoubleType(), True),
        ])
        
        df = spark.createDataFrame(data, schema=schema)
        print(f"  ✅ Created DataFrame with {df.count()} rows")
        
        # Show sample data
        print("\nSample data:")
        df.show()
        
        # Create Nessie/Iceberg table
        print("\n2️⃣  Creating Iceberg table on Nessie...")
        table_name = "nessie.sample_employees"
        
        # Drop table if exists
        try:
            spark.sql(f"DROP TABLE IF EXISTS {table_name}")
            print(f"  Dropped existing table: {table_name}")
        except:
            pass
        
        # Write to Nessie as Iceberg table
        df.write.format("iceberg").mode("overwrite").saveAsTable(table_name)
        print(f"  ✅ Created table: {table_name}")
        
        # Query the table
        print("\n3️⃣  Querying the table...")
        result_df = spark.sql(f"SELECT * FROM {table_name} WHERE salary > 75000")
        print(f"  Found {result_df.count()} employees with salary > 75000:")
        result_df.show()
        
        # Aggregation
        print("\n4️⃣  Aggregation query...")
        agg_df = spark.sql(f"""
            SELECT 
                COUNT(*) as total_employees,
                AVG(salary) as avg_salary,
                MAX(salary) as max_salary,
                MIN(salary) as min_salary
            FROM {table_name}
        """)
        print("  Salary statistics:")
        agg_df.show()
        
        # Show table schema
        print("\n5️⃣  Table schema:")
        spark.sql(f"DESCRIBE {table_name}").show()
        
        print("\n" + "=" * 80)
        print("✅ ETL job completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during ETL: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        spark.stop()
    
    return 0

if __name__ == "__main__":
    exit(main())
