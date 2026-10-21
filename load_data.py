import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    sslmode=os.getenv("DB_SSLMODE")
)

cur = conn.cursor()

print("Connected to PostgreSQL!")

products = pd.read_csv("data/products_clean.csv")
reviews = pd.read_csv("data/reviews_clean.csv")

print("Products to load:", len(products))
print("Reviews to load:", len(reviews))

# Convert 0/1 indicators to booleans, preserving missing values
products["sephora_exclusive"] = (
    products["sephora_exclusive"].map({0: False, 1: True})
)

reviews["is_recommended"] = (
    reviews["is_recommended"].map({0: False, 1: True})
)

# Convert dates to Python date objects
reviews["submission_time"] = pd.to_datetime(
    reviews["submission_time"]
).dt.date

# Replace missing values with Python None (SQL NULL)
products = products.astype(object).where(pd.notna(products), None)
reviews = reviews.astype(object).where(pd.notna(reviews), None)

product_sql = """
INSERT INTO products (
    product_id,
    product_name,
    brand_name,
    price_usd,
    rating,
    loves_count,
    primary_category,
    secondary_category,
    sephora_exclusive
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (product_id) DO NOTHING;
"""

execute_batch(
    cur,
    product_sql,
    list(products.itertuples(index=False, name=None)),
    page_size=500
)

print("Products inserted!")

# Reset review rows so rerunning produces the same dataset
cur.execute("TRUNCATE TABLE reviews RESTART IDENTITY;")

review_sql = """
INSERT INTO reviews (
    product_id,
    author_id,
    rating,
    is_recommended,
    submission_time,
    review_text,
    skin_type
)
VALUES (%s, %s, %s, %s, %s, %s, %s);
"""

execute_batch(
    cur,
    review_sql,
    list(reviews.itertuples(index=False, name=None)),
    page_size=500
)

print("Reviews inserted!")

conn.commit()

cur.execute("SELECT COUNT(*) FROM products;")
print("Products in database:", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM reviews;")
print("Reviews in database:", cur.fetchone()[0])

cur.close()
conn.close()

print("Data loading complete!")