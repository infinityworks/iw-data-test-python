import csv
import json
import math
import os
import random
from datetime import timedelta

import numpy as np


class Customer(object):
    def __init__(self, customer_id, loyalty_score):
        self.customer_id = customer_id
        self.value_score = loyalty_score


def generate_customers(output_location_root, number_of_customers, return_data=True):
    customers = []
    with open(f'{output_location_root}/customers.csv', mode='w') as customers_file:
        csv_writer = csv.writer(customers_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(["customer_id", "loyalty_score"])
        for cid in range(1, number_of_customers + 1):
            score = np.random.randint(low=1, high=11)
            customer_id = f"C{cid}"
            csv_writer.writerow([customer_id, score])
            if return_data:
                customers.append(Customer(customer_id, score))
    return customers if return_data else None


def generate_products(output_location_root, products_to_generate):
    product_count_digits = int(math.log10(len(sum(products_to_generate.values(), []))) + 1)

    product_id_lookup = {k: {} for k, v in products_to_generate.items()}
    with open(f'{output_location_root}/products.csv', mode='w') as products_file:
        csv_writer = csv.writer(products_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(["product_id", "product_description", "product_category"])
        item_index = 1
        for category in products_to_generate:
            for item in products_to_generate[category]:
                product_id = f"P{str(item_index).zfill(product_count_digits)}"
                csv_writer.writerow([product_id, item, category])
                product_id_lookup[category][item] = product_id
                item_index += 1
    return product_id_lookup


def generate_transactions(output_location_root, customers, products, product_id_lookup, products_cats_frequency,
                          start_datetime, end_datetime):
    open_files = open_transaction_sinks(output_location_root, start_datetime, end_datetime)
    product_cats_count = len(products.keys())
    num_days = (end_datetime - start_datetime).days
    all_days = [start_datetime + timedelta(days=d) for d in range(0, num_days + 1)]
    customer_frequency_type = [int(num_days / 14), int(num_days / 10), int(num_days / 7), int(num_days / 5),
                               int(num_days / 4), int(num_days / 3)]

    for customer in customers:
        num_transaction_days = random.choice(customer_frequency_type)
        num_cats = random.randint(1, product_cats_count)
        customer_transaction_days = sorted(random.sample(all_days, num_transaction_days))
        cats = random.sample(products_cats_frequency, num_cats)
        for day in customer_transaction_days:
            transaction = {
                "customer_id": customer.customer_id,
                "basket": generate_basket(products, product_id_lookup, cats),
                "date_of_purchase": str(day + timedelta(minutes=random.randint(168, 1439)))
            }
            open_files[to_canonical_date_str(day)].write(json.dumps(transaction) + "\n")

    for f in open_files.values():
        f.close()


def to_canonical_date_str(date_to_transform):
    return date_to_transform.strftime('%Y-%m-%d')


def open_transaction_sinks(output_location_root, start_datetime, end_datetime):
    root_transactions_dir = f"{output_location_root}/transactions/"
    open_files = {}
    days_to_generate = (end_datetime - start_datetime).days
    for next_day_offset in range(0, days_to_generate + 1):
        next_day = to_canonical_date_str(start_datetime + timedelta(days=next_day_offset))
        day_directory = f"{root_transactions_dir}/d={next_day}"
        os.makedirs(day_directory, exist_ok=True)
        open_files[next_day] = open(f"{day_directory}/transactions.json", mode='w')
    return open_files


def generate_basket(products, product_id_lookup, cats):
    num_items_in_basket = random.randint(1, 3)
    basket = []
    product_category = random.choice(cats)
    for item in [random.choice(products[product_category]) for _ in range(0, num_items_in_basket)]:
        product_id = product_id_lookup[product_category][item]
        basket.append({
            "product_id": product_id,
            "price": random.randint(1, 2000)
        })
    return basket
