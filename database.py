
import os
import re
from contextlib import closing

import pandas as pd
import psycopg2

from pglast import parse_sql, ast


# Reject potentially dangerous SQL commands.
BLOCKED = re.compile(
    r"\b(?:INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|"
    r"GRANT|REVOKE|COPY|CALL|DO|EXECUTE|PREPARE|SET|RESET|"
    r"VACUUM|ANALYZE|EXPLAIN|LOCK|INTO|PG_SLEEP|"
    r"PG_READ_FILE|PG_LS_DIR)\b",
    flags=re.IGNORECASE,
)



def validate_sql(query):
    query = query.strip()

    if not query:
        raise ValueError("Please enter a SQL query.")

    if len(query) > 10000:
        raise ValueError("Query is too long.")

    try:
        statements = parse_sql(query)
    except Exception:
        raise ValueError("Invalid SQL syntax.")

    if len(statements) != 1:
        raise ValueError("Only one SQL statement is allowed.")

    statement = statements[0].stmt

    if not isinstance(statement, ast.SelectStmt):
        raise ValueError("Only SELECT queries are allowed.")

    # Defense in depth: reject suspicious commands and functions.
    if BLOCKED.search(query):
        raise ValueError("This SQL command is not allowed.")

    return query



def run_query(query):
    query = validate_sql(query)

    with closing(psycopg2.connect(
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["QUIZ_DB_USER"],
        password=os.environ["QUIZ_DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        sslmode=os.environ.get("DB_SSLMODE", "require"),
        connect_timeout=8,
    )) as conn:

        conn.set_session(readonly=True, autocommit=False)

        with conn.cursor() as cur:
            cur.execute("SET LOCAL statement_timeout = '5000ms'")
            cur.execute("SET LOCAL search_path = public, pg_catalog")

            cur.execute(query)

            if cur.description is None:
                raise ValueError("Query returned no result table.")

            columns = [col.name for col in cur.description]
            rows = cur.fetchmany(201)

            if len(rows) > 200:
                raise ValueError(
                    "More than 200 rows returned. "
                    "Please add a LIMIT or aggregate your results."
                )

            return pd.DataFrame(rows, columns=columns)
