import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("QUIZ_DB_USER"),
    password=os.getenv("QUIZ_DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    sslmode=os.getenv("DB_SSLMODE")
)

cur = conn.cursor()

cur.execute("SELECT current_user;")
print("Connected as:", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM public.products;")
print("Products:", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM public.reviews;")
print("Reviews:", cur.fetchone()[0])

# Test whether quiz_reader can modify the database
try:
    cur.execute("""
        DELETE FROM public.products
        WHERE product_id = 'TEST_NONEXISTENT_PRODUCT';
    """)
    print("WARNING: DELETE was allowed!")

except (
    psycopg2.errors.InsufficientPrivilege,
    psycopg2.errors.ReadOnlySqlTransaction
):
    print("SUCCESS: DELETE was blocked!")

finally:
    conn.rollback()

cur.close()
conn.close()