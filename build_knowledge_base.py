
from pathlib import Path

import chromadb

from questions import QUESTIONS


CHROMA_PATH = Path("chroma_data")
COLLECTION_NAME = "sephora_sql_knowledge"


def build_documents():
    documents = [
        {
            "id": "products_schema",
            "text": """
            Table: products
            Primary key: product_id

            Columns:
            product_id TEXT
            product_name TEXT
            brand_name TEXT
            price_usd NUMERIC
            rating NUMERIC
            loves_count INTEGER
            primary_category TEXT
            secondary_category TEXT
            sephora_exclusive BOOLEAN

            Each row represents one Sephora product.
            Use this table for product, brand, price,
            rating, and category questions.
            """,
        },
        {
            "id": "reviews_schema",
            "text": """
            Table: reviews
            Primary key: review_id

            Columns:
            review_id BIGINT
            product_id TEXT
            author_id TEXT
            rating INTEGER
            is_recommended BOOLEAN
            submission_time DATE
            review_text TEXT
            skin_type TEXT

            Each row represents one customer review.
            Use this table for review counts, customer
            recommendations, and skin type analysis.
            """,
        },
        {
            "id": "table_relationships",
            "text": """
            The reviews table has a foreign key:
            reviews.product_id references products.product_id.

            One product can have many reviews.

            Join example:
            SELECT p.brand_name, COUNT(*) AS review_count
            FROM products AS p
            JOIN reviews AS r
                ON p.product_id = r.product_id
            GROUP BY p.brand_name;

            An INNER JOIN excludes products with no reviews.
            """,
        },
        {
            "id": "business_rules",
            "text": """
            Business rules:

            The reviews table contains 10,000 sampled reviews,
            not all Sephora reviews.

            For recommendation rates, is_recommended = TRUE
            represents a positive recommendation.

            Exclude NULL recommendation values when calculating
            recommendation percentages.

            Use NULLIF to protect denominators from division by zero.

            Use PostgreSQL syntax.

            For ranking products within categories,
            ROW_NUMBER() can be used with PARTITION BY.

            For products without reviews, consider NOT EXISTS.
            """,
        },
    ]

    # Add the five quiz questions as few-shot examples.
    for question in QUESTIONS:
        documents.append(
            {
                "id": f"quiz_example_{question['id']}",
                "text": (
                    f"Example question: {question['title']}\n"
                    f"Business question: {question['prompt']}\n"
                    f"SQL concepts: {question['pattern']}\n"
                    f"Reference PostgreSQL SQL:\n"
                    f"{question['solution']}"
                ),
            }
        )

    return documents


def main():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    documents = build_documents()

    collection.upsert(
        ids=[document["id"] for document in documents],
        documents=[document["text"] for document in documents],
    )

    print(f"Indexed {collection.count()} knowledge documents.")


if __name__ == "__main__":
    main()
