from datetime import datetime

import pytest
from pyspark import Row

from solution.solution_start import get_latest_transaction_date


@pytest.mark.usefixtures("spark")
def test_get_latest_transaction_date_returns_most_recent_date(spark):
    spark.createDataFrame([
        Row(date_of_purchase=datetime(2018, 12, 1, 4, 15, 0)),
        Row(date_of_purchase=datetime(2019, 3, 1, 14, 10, 0)),
        Row(date_of_purchase=datetime(2019, 2, 1, 14, 9, 59)),
        Row(date_of_purchase=datetime(2019, 1, 2, 19, 14, 20))
    ]).createOrReplaceTempView("raw_transactions")

    expected = datetime(2019, 3, 1, 14, 10, 0)
    actual = get_latest_transaction_date(spark)

    assert actual == expected
