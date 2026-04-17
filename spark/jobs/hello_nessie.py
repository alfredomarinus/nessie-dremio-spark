#!/usr/bin/env python3
"""
Hello Spark with Nessie - Cluster health check and Nessie connectivity test.
Validates Spark cluster is operational and can connect to Nessie/Iceberg.
"""

from pyspark.sql import SparkSession

def main():
    # Initialize Spark session with Nessie catalog
    spark = SparkSession.builder \
        .appName("hello-nessie") \
        .getOrCreate()
    
    print("=" * 80)
    print("Hello Spark + Nessie! Testing cluster connectivity...")
    print("=" * 80)
    
    # Get Spark configuration
    spark_config = spark.sparkContext.getConf().getAll()
    print(f"\nSpark Configuration ({len(spark_config)} items):")
    for key, value in sorted(spark_config):
        if not any(secret in key.lower() for secret in ['password', 'secret', 'key']):
            print(f"  {key}: {value}")
    
    # Get Spark context information
    print(f"\nSpark Context Information:")
    print(f"  App Name: {spark.sparkContext.appName}")
    print(f"  App ID: {spark.sparkContext.applicationId}")
    print(f"  Master: {spark.sparkContext.master}")
    print(f"  Default Parallelism: {spark.sparkContext.defaultParallelism}")
    print(f"  Default Min Partitions: {spark.sparkContext.defaultMinPartitions}")
    
    # Test Nessie connectivity
    print(f"\nTesting Nessie Catalog:")
    try:
        # List branches
        branches_df = spark.sql("SELECT * FROM nessie.branches")
        print(f"  ✅ Connected to Nessie")
        print(f"  Available branches:")
        for row in branches_df.collect():
            print(f"    - {row}")
    except Exception as e:
        print(f"  ⚠️  Could not list branches: {e}")
    
    # Simple data processing
    print(f"\nRunning simple Spark SQL:")
    data = [1, 2, 3, 4, 5]
    rdd = spark.sparkContext.parallelize(data)
    result = rdd.map(lambda x: x * 2).collect()
    print(f"  Input: {data}")
    print(f"  Transformed (x*2): {result}")
    print(f"  Sum: {sum(result)}")
    
    print("\n" + "=" * 80)
    print("✅ Job completed successfully!")
    print("=" * 80)
    
    spark.stop()

if __name__ == "__main__":
    main()
