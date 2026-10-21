QUESTIONS = [
    {
        "id": 1,
        "title": "Finding Products Without Reviews",
        "difficulty": "Easy",
        "points": 4,
        "pattern": "NOT EXISTS",
        "prompt": (
            "The merchandising team wants to identify products that have "
            "not received any reviews in the available dataset.\n\n"
            "Return product_id, product_name, and brand_name for products "
            "with no matching reviews. Order by product_id ascending "
            "and return the first 10."
        ),
        "hint": (
            "Consider using NOT EXISTS with a correlated "
            "subquery to find products without matching reviews."
        ),
        "solution": """
SELECT p.product_id, p.product_name, p.brand_name
FROM products AS p
WHERE NOT EXISTS (
    SELECT 1
    FROM reviews AS r
    WHERE r.product_id = p.product_id
)
ORDER BY p.product_id
LIMIT 10;
""",
        "expected": "10 products with no reviews in the sample.",
    },
    {
        "id": 2,
        "title": "Identifying Highly Reviewed Brands",
        "difficulty": "Easy–Medium",
        "points": 4,
        "pattern": "JOIN, GROUP BY, HAVING",
        "prompt": (
            "The customer insights team wants to identify brands "
            "receiving substantial customer feedback.\n\n"
            "Find brands with at least 100 sampled reviews. "
            "Return brand_name and review_count. Sort by review_count "
            "descending, then brand_name ascending."
        ),
        "hint": (
            "JOIN products and reviews, then use GROUP BY "
            "and HAVING to filter brands by review count."
        ),
        "solution": """
SELECT
    p.brand_name,
    COUNT(*) AS review_count
FROM reviews AS r
JOIN products AS p
    ON r.product_id = p.product_id
GROUP BY p.brand_name
HAVING COUNT(*) >= 100
ORDER BY review_count DESC, p.brand_name;
""",
        "expected": "One row per qualifying brand and its review count.",
    },
    {
        "id": 3,
        "title": "Comparing Recommendations by Skin Type",
        "difficulty": "Medium",
        "points": 4,
        "pattern": "Conditional aggregation",
        "prompt": (
            "The product research team wants to understand how "
            "recommendations vary by skin type.\n\n"
            "For each non-null skin type, calculate total_reviews, "
            "recommended, and not_recommended. Exclude reviews where "
            "is_recommended is NULL. Sort alphabetically by skin_type."
        ),
        "hint": (
            "Use conditional aggregation with CASE WHEN "
            "to count recommended and non-recommended reviews."
        ),
        "solution": """
SELECT
    skin_type,
    COUNT(*) AS total_reviews,
    SUM(
        CASE WHEN is_recommended = TRUE
            THEN 1 ELSE 0 END
    ) AS recommended,
    SUM(
        CASE WHEN is_recommended = FALSE
            THEN 1 ELSE 0 END
    ) AS not_recommended
FROM reviews
WHERE skin_type IS NOT NULL
  AND is_recommended IS NOT NULL
GROUP BY skin_type
ORDER BY skin_type;
""",
        "expected": (
            "One row per skin type with total review counts, "
            "recommended counts, and not-recommended counts."
        ),
    },
    {
        "id": 4,
        "title": "Calculating Brand Recommendation Rates",
        "difficulty": "Medium–Hard",
        "points": 4,
        "pattern": "Rates and NULL-safe division",
        "prompt": (
            "The analytics team wants to compare customer satisfaction "
            "across brands.\n\n"
            "For each brand, calculate the percentage of reviews "
            "marked TRUE among reviews with non-null is_recommended. "
            "Include brands with at least 30 such reviews. "
            "Return brand_name, total_reviews, and recommendation_rate "
            "rounded to two decimals. Sort by rate descending, "
            "then brand name ascending."
        ),
        "hint": (
            "Calculate the percentage of TRUE recommendations "
            "using conditional aggregation. Consider NULLIF "
            "to protect against division by zero."
        ),
        "solution": """
SELECT
    p.brand_name,
    COUNT(*) AS total_reviews,
    ROUND(
        100.0 * SUM(
            CASE WHEN r.is_recommended = TRUE
                THEN 1 ELSE 0 END
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS recommendation_rate
FROM reviews AS r
JOIN products AS p
    ON r.product_id = p.product_id
WHERE r.is_recommended IS NOT NULL
GROUP BY p.brand_name
HAVING COUNT(*) >= 30
ORDER BY recommendation_rate DESC, p.brand_name;
""",
        "expected": (
            "One row per qualifying brand showing its eligible "
            "review count and recommendation percentage, "
            "ranked from highest to lowest."
        ),
    },
    {
        "id": 5,
        "title": "Finding the Top Product in Each Category",
        "difficulty": "Hard",
        "points": 4,
        "pattern": "CTEs and ROW_NUMBER",
        "prompt": (
            "The merchandising team wants to feature the most-loved "
            "product in each primary category.\n\n"
            "Return primary_category, product_name, brand_name, and "
            "loves_count for the product with the highest loves_count "
            "in each non-null category. Break ties using the "
            "alphabetically first product_id. Sort by category."
        ),
        "hint": (
            "Use ROW_NUMBER() with PARTITION BY to rank "
            "products within each primary category. "
            "A CTE can help you filter to the top product."
        ),
        "solution": """
WITH ranked_products AS (
    SELECT
        primary_category,
        product_name,
        brand_name,
        loves_count,
        ROW_NUMBER() OVER (
            PARTITION BY primary_category
            ORDER BY
                loves_count DESC NULLS LAST,
                product_id ASC
        ) AS rn
    FROM products
    WHERE primary_category IS NOT NULL
)
SELECT
    primary_category,
    product_name,
    brand_name,
    loves_count
FROM ranked_products
WHERE rn = 1
ORDER BY primary_category;
""",
        "expected": (
            "One row per primary category showing the product "
            "with the highest loves_count."
        ),
    },
]
