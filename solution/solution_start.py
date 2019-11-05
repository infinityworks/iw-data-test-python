import argparse

from pyspark.sql import SparkSession


def create_spark_views(spark: SparkSession, customers_location: str, products_location: str,
                       transactions_location: str):
    spark.read.csv(customers_location, header=True).createOrReplaceTempView("customers")
    spark.read.csv(products_location, header=True).createOrReplaceTempView("products")
    spark.read.json(transactions_location).createOrReplaceTempView("raw_transactions")


def run_transformations(spark: SparkSession, customers_location: str, products_location: str,
                        transactions_location: str, output_location: str):
    create_spark_views(spark, customers_location, products_location, transactions_location)


def get_latest_transaction_date(spark: SparkSession):
    result = spark.sql("""SELECT MAX(date_of_purchase) AS date_of_purchase FROM raw_transactions""").collect()[0]
    max_date = result.date_of_purchase
    return max_date


def to_canonical_date_str(date_to_transform):
    return date_to_transform.strftime('%Y-%m-%d')


if __name__ == "__main__":
    spark_session = (
            SparkSession.builder
                        .master("local[2]")
                        .appName("DataTest")
                        .config("spark.executorEnv.PYTHONHASHSEED", "0")
                        .getOrCreate()
    )

    parser = argparse.ArgumentParser(description='DataTest')
    parser.add_argument('--customers_location', required=False, default="./input_data/starter/customers.csv")
    parser.add_argument('--products_location', required=False, default="./input_data/starter/products.csv")
    parser.add_argument('--transactions_location', required=False, default="./input_data/starter/transactions/")
    parser.add_argument('--output_location', required=False, default="./output_data/outputs/")
    args = vars(parser.parse_args())

    run_transformations(spark_session, args['customers_location'], args['products_location'],
                        args['transactions_location'], args['output_location'])
