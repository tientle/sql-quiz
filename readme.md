# Sephora SQL Lab

[![Sephora SQL Lab Tests](https://github.com/tientle/sql-quiz/actions/workflows/tests.yml/badge.svg)](https://github.com/tientle/sql-quiz/actions/workflows/tests.yml)

![Sephora SQL Lab](https://img.shields.io/badge/Sephora_SQL_Lab-Interactive_Quiz-FF69B4)
![PostgreSQL](https://img.shields.io/badge/SQL-PostgreSQL-DB7093)
![Streamlit](https://img.shields.io/badge/Built_with-Streamlit-FFB6C1)

An interactive SQL quiz application built with Python, Streamlit, PostgreSQL, and Supabase.

Sephora SQL Lab allows students to practice SQL using real-world Sephora product and customer review data. Users can sign in, answer interview-style SQL questions, execute queries against a hosted PostgreSQL database, view live results, and save their answers.

## Live Application and Repository

**Live Application:** [Sephora SQL Lab](https://sephora-sql-quiz.streamlit.app/)

**GitHub Actions:** [View Workflow Runs](https://github.com/tientle/sql-quiz/actions)

### Grader Access

The application requires authentication to access the SQL quiz.

A dedicated account has been created for assignment evaluation.

- **Email:** `grader@example.com`
- **Password:** Provided separately through the private Canvas submission
- **Registration:** Not required

The grader can use this account to sign in, access all five questions, execute SQL queries, view expected results, and save answers.

The password is intentionally excluded from this public repository.

---

## Project Overview

The goal of this project is to create an interactive SQL assessment environment similar to a classroom exercise or technical interview.

Instead of working with static examples, students write SQL queries that execute against a live PostgreSQL database.

The questions use Sephora product and customer review data to explore realistic business problems involving merchandising, customer insights, and product analytics.

### Key Features

- Hosted PostgreSQL database containing Sephora products and reviews
- User authentication through Supabase Auth
- Five SQL questions worth a total of 20 points
- Interactive SQL editor
- Live query execution and result tables
- Conceptual hints and reference SQL solutions
- Expected output rows generated from the database
- Persistent answer storage for authenticated users
- Database schema reference
- Automated testing through GitHub Actions
- Deployment through Streamlit Community Cloud

## 1. Hosted Database

### 1.1 Database Hosting

The application uses PostgreSQL hosted on Supabase.

Supabase provides a managed PostgreSQL instance that stores the Sephora dataset and supports SQL execution over a network connection.

The Streamlit application connects to PostgreSQL using Python's `psycopg2` library.

The connection uses the Supabase Session Pooler with SSL enabled (`sslmode=require`).

### 1.2 Dataset Overview

The project uses the Kaggle Sephora Products and Skincare Reviews dataset.

A subset of the original data was loaded into PostgreSQL.

| Table      |   Rows | Description                                                            |
| ---------- | -----: | ---------------------------------------------------------------------- |
| `products` |  8,494 | Product information, including brands, prices, ratings, and categories |
| `reviews`  | 10,000 | Sampled customer reviews, ratings, recommendations, and skin types     |

The database supports joins, aggregations, subqueries, and window functions.

### 1.3 Database Schema

#### Products Table

| Column               | Data Type     | Description                                 |
| -------------------- | ------------- | ------------------------------------------- |
| `product_id`         | TEXT          | Unique product identifier; primary key      |
| `product_name`       | TEXT          | Product name                                |
| `brand_name`         | TEXT          | Product brand                               |
| `price_usd`          | NUMERIC(10,2) | Product price in US dollars                 |
| `rating`             | NUMERIC       | Product rating                              |
| `loves_count`        | INTEGER       | Number of user loves                        |
| `primary_category`   | TEXT          | Primary product category                    |
| `secondary_category` | TEXT          | Secondary product category                  |
| `sephora_exclusive`  | BOOLEAN       | Whether the product is exclusive to Sephora |

#### Reviews Table

| Column            | Data Type | Description                                   |
| ----------------- | --------- | --------------------------------------------- |
| `review_id`       | BIGINT    | Unique review identifier; primary key         |
| `product_id`      | TEXT      | Foreign key referencing `products.product_id` |
| `author_id`       | TEXT      | Reviewer identifier                           |
| `rating`          | INTEGER   | Customer rating                               |
| `is_recommended`  | BOOLEAN   | Whether the reviewer recommends the product   |
| `submission_time` | DATE      | Review submission date                        |
| `review_text`     | TEXT      | Written review                                |
| `skin_type`       | TEXT      | Customer skin type                            |

### 1.4 Table Relationships

The database uses a one-to-many relationship between products and reviews.

Each product can have multiple reviews, and each review references a product through `product_id`.

Example query:

```sql
SELECT
    p.brand_name,
    COUNT(*) AS review_count
FROM reviews AS r
JOIN products AS p
    ON r.product_id = p.product_id
GROUP BY p.brand_name
ORDER BY review_count DESC;
```

This query joins the tables and calculates the number of sampled reviews for each brand.

### 1.5 Database Connection and Query Execution

The `database.py` module handles database connections, SQL validation, and query execution.

When a user submits SQL:

1. The application receives the query from the Streamlit editor.
2. The query is passed to the database execution module.
3. The application validates the query.
4. A restricted PostgreSQL connection executes the query.
5. PostgreSQL returns the result set.
6. Streamlit displays the returned rows.

The application is designed for read-only analytical queries.

### 1.6 Database Security

A dedicated PostgreSQL role named `quiz_reader` is used for executing quiz queries.

This role has SELECT permissions on the `products` and `reviews` tables.

Additional protections include:

- Read-only transactions
- A five-second statement timeout
- SQL query validation
- A limit on returned result rows
- Database credentials stored outside the source code

These measures reduce the risk of unauthorized data modification and resource-intensive queries.

However, read-only permissions and SQL validation do not provide complete isolation for arbitrary SQL execution. Additional sandboxing would be needed for unrestricted public use.

---

## 2. Authentication

### 2.1 Supabase Authentication

The application uses Supabase Auth for email/password authentication.

Supabase manages authentication sessions and assigns each user a unique identifier.

Users must authenticate before accessing the SQL quiz.

### 2.2 Access Restrictions

Signed-out users cannot:

- Access the quiz interface
- Execute SQL queries
- Save SQL answers

Signed-in users can:

- Select quiz questions
- Write and execute SQL
- View query results
- Save answers
- Retrieve previously saved answers

The application verifies the authenticated user session before protected operations.

### 2.3 Answer Storage

Saved SQL answers are stored in a Supabase table named `quiz_answers`.

| Column        | Description                                |
| ------------- | ------------------------------------------ |
| `id`          | Unique answer identifier                   |
| `user_id`     | Authenticated user's ID                    |
| `question_id` | Corresponding quiz question                |
| `sql_answer`  | Saved SQL query                            |
| `updated_at`  | Timestamp associated with the saved record |

A unique constraint on `(user_id, question_id)` allows users to update their existing answers.

### 2.4 Row Level Security

Supabase Row Level Security (RLS) policies are enabled on `quiz_answers`.

These policies restrict authenticated users to reading, inserting, and updating their own answers.

Saved answers are associated with the authenticated user's ID rather than being shared across accounts.

### 2.5 Answer Persistence

When users click **Save Answer**, their SQL is stored in Supabase.

When they sign out and return later, their previously saved answers are loaded into the editor.

This allows users to resume their work across sessions.

### 2.6 Grader Access

A dedicated test account has been created to allow the instructor or grader to evaluate the application.

**Login email:** `grader@example.com`

**Password:** Provided privately through Canvas.

The grader can:

1. Sign in to the deployed application.
2. Select any of the five SQL questions.
3. Execute SQL queries against the hosted database.
4. View live query results.
5. Review hints and reference solutions.
6. Display expected output rows.
7. Save answers and verify persistence.

No additional account registration is required.

---

## 3. GitHub Actions

### 3.1 Continuous Integration Workflow

The project uses GitHub Actions for automated testing.

The workflow is located at:

```text
.github/workflows/tests.yml
```

The workflow runs when code is pushed to GitHub or a pull request is opened.

**Workflow History:** [View GitHub Actions](https://github.com/tientle/sql-quiz/actions)

### 3.2 Automated Tests

The workflow performs the following checks:

1. Checks out the repository.
2. Configures Python 3.11.
3. Installs the dependencies required for testing.
4. Checks that the application Python files compile.
5. Verifies that the quiz contains five questions.
6. Confirms that question point values total 20.
7. Checks that question IDs are unique.
8. Verifies that required question content is present.
9. Connects to the hosted PostgreSQL database.
10. Confirms that the database contains 8,494 products and 10,000 reviews.

These checks validate both the application structure and the hosted database connection.

### 3.3 GitHub Secrets

The workflow uses GitHub Repository Secrets to store database connection credentials.

Configured secrets include:

- `POSTGRES_DB`
- `DB_HOST`
- `DB_PORT`
- `DB_SSLMODE`
- `QUIZ_DB_USER`
- `QUIZ_DB_PASSWORD`

The workflow references these values through environment variables.

No database password is committed to the repository or hardcoded in the workflow.

### 3.4 Successful Workflow Verification

The GitHub Actions workflow completed successfully during development.

The database connection test demonstrates that the workflow can access the hosted PostgreSQL database using credentials supplied through GitHub Secrets.

Workflow execution history is available in the repository's Actions tab.

---

## 4. SQL Quiz

### 4.1 Quiz Overview

The quiz contains five questions worth four points each, totaling 20 points.

Questions increase in difficulty and cover SQL concepts commonly used in data analytics and technical interviews.

Each question is framed around a business problem involving Sephora products, customer reviews, or merchandising decisions.

### 4.2 Quiz Questions

| Question                                 | Difficulty  | SQL Concepts                       | Points |
| ---------------------------------------- | ----------- | ---------------------------------- | -----: |
| Finding Products Without Reviews         | Easy        | NOT EXISTS, correlated subqueries  |      4 |
| Identifying Highly Reviewed Brands       | Easy–Medium | JOIN, GROUP BY, HAVING             |      4 |
| Comparing Recommendations by Skin Type   | Medium      | CASE WHEN, conditional aggregation |      4 |
| Calculating Brand Recommendation Rates   | Medium–Hard | Aggregation, percentages, NULLIF   |      4 |
| Finding the Top Product in Each Category | Hard        | CTEs, ROW_NUMBER, window functions |      4 |
| **Total**                                |             |                                    | **20** |

### 4.3 Question Structure

Each question includes:

- A descriptive title
- A difficulty level
- A point value
- A realistic business scenario
- Required output columns and sorting instructions
- A conceptual hint
- A reference SQL solution
- An expected result description
- Expected output rows generated from the database

Questions are defined in `questions.py`.

### 4.4 Live SQL Execution

Authenticated users can write SQL queries in the Streamlit editor.

Clicking **Run Query** sends the query to PostgreSQL.

The application displays the returned rows in an interactive table.

Users can revise their SQL and rerun queries to compare results.

### 4.5 Hints and Expected Results

Each question includes two expandable reference sections.

#### Show Hint

Displays a conceptual clue suggesting an SQL technique that may help solve the question.

#### Show Expected SQL & Results

Displays:

- The reference SQL solution
- A description of the expected result
- A button to display actual expected output rows

Clicking **Show Expected Output Rows** executes the reference SQL query against the hosted database and displays the results.

This allows users to compare their own output with the expected output.

The assignment evaluates SQL result sets rather than requiring users to reproduce the reference SQL exactly.

### 4.6 How to Use the Quiz

**Step 1: Open the application**

Visit [Sephora SQL Lab](https://sephora-sql-quiz.streamlit.app/).

**Step 2: Sign in**

Enter your registered email and password.

For assignment evaluation, use the dedicated grader account credentials provided through Canvas.

**Step 3: Select a question**

Choose one of the five questions from the dropdown menu.

**Step 4: Review the schema**

Use the database reference in the sidebar to inspect available tables, columns, and data types.

**Step 5: Write SQL**

Enter your SQL query in the editor.

**Step 6: Execute the query**

Click **Run Query** to execute the query and view its results.

**Step 7: Save your answer**

Click **Save Answer** to store your SQL query in Supabase.

**Step 8: Review expected results**

Expand the hint and reference solution sections as needed.

Click **Show Expected Output Rows** to view the output from the reference SQL query.

### 4.7 Quiz Grading

The quiz is worth 20 points based on the assigned question values.

The application provides reference solutions and expected results for comparison.

SQL answers are saved but are not automatically graded.

---

## 5. README and Project Documentation (15 Points)

### 5.1 Technology Stack

| Technology                | Purpose                         |
| ------------------------- | ------------------------------- |
| Python                    | Application logic               |
| Streamlit                 | Interactive web interface       |
| Supabase PostgreSQL       | Hosted relational database      |
| Supabase Auth             | User authentication             |
| psycopg2                  | PostgreSQL connectivity         |
| Pandas                    | Handling query results          |
| python-dotenv             | Local environment configuration |
| GitHub                    | Version control                 |
| GitHub Actions            | Automated testing               |
| Streamlit Community Cloud | Application deployment          |

### 5.2 Application Architecture

The application contains four main components.

**Streamlit Frontend**

Provides the login interface, question selection, SQL editor, query results, hints, and answer-saving controls.

**Supabase Authentication**

Authenticates users and manages access to protected functionality.

**Supabase PostgreSQL**

Stores the Sephora product and review data, executes SQL queries, and stores saved quiz answers.

**GitHub Actions**

Runs automated checks against the codebase and hosted database.

### 5.3 Project Structure

```text
sql-quiz/
├── .github/
│   └── workflows/
│       └── tests.yml
├── app.py
├── database.py
├── questions.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

The `.env` file is used locally and is not committed to GitHub.

| File                          | Purpose                                                     |
| ----------------------------- | ----------------------------------------------------------- |
| `app.py`                      | Streamlit interface, authentication, and answer persistence |
| `database.py`                 | PostgreSQL connections, SQL validation, and query execution |
| `questions.py`                | Quiz questions, hints, reference SQL, and expected results  |
| `requirements.txt`            | Python dependencies                                         |
| `.github/workflows/tests.yml` | Automated testing workflow                                  |
| `.gitignore`                  | Files excluded from version control                         |
| `.env`                        | Local credentials                                           |
| `README.md`                   | Project documentation                                       |

### 5.4 Local Setup

#### Prerequisites

- Python 3.11 or compatible version
- Git
- A configured Supabase project
- PostgreSQL tables containing the Sephora data
- Supabase authentication configuration
- Appropriate database roles and permissions

#### Clone the Repository

```bash
git clone PASTE_YOUR_GITHUB_REPOSITORY_URL_HERE
cd sql-quiz
```

#### Create a Virtual Environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

### 5.5 Environment Variables

Create a `.env` file in the project root.

Use the following template:

```dotenv
POSTGRES_DB=postgres
POSTGRES_USER=postgres.YOUR_PROJECT_REF
POSTGRES_PASSWORD=YOUR_DATABASE_PASSWORD

DB_HOST=YOUR_SUPABASE_SESSION_POOLER_HOST
DB_PORT=5432
DB_SSLMODE=require

SUPABASE_URL=YOUR_SUPABASE_PROJECT_URL
SUPABASE_KEY=YOUR_SUPABASE_PUBLISHABLE_KEY

QUIZ_DB_USER=quiz_reader.YOUR_PROJECT_REF
QUIZ_DB_PASSWORD=YOUR_RESTRICTED_ROLE_PASSWORD
```

Replace the placeholders with credentials from your Supabase project.

The `SUPABASE_KEY` should be a publishable or anonymous client key, not a service-role key.

Do not commit `.env` to GitHub.

The database tables, authentication configuration, and permissions must already exist for the application to run locally.

### 5.6 Running the Application Locally

Start Streamlit:

```bash
streamlit run app.py
```

Streamlit typically starts the application at:

```text
http://localhost:8501
```

Open the URL in your browser to access the quiz.

### 5.7 Deployment

The application is deployed through Streamlit Community Cloud.

Deployment configuration:

| Setting      | Value              |
| ------------ | ------------------ |
| Source       | GitHub repository  |
| Branch       | `main`             |
| Main file    | `app.py`           |
| Dependencies | `requirements.txt` |
| Credentials  | Streamlit Secrets  |

The deployed application connects to Supabase PostgreSQL over the network.

Sensitive credentials are stored in Streamlit Secrets rather than the repository.

Updates pushed to the configured GitHub branch are reflected in the deployed application after Streamlit redeploys.

### 5.8 Testing and Verification

The following functionality was tested during development:

- User authentication through Supabase Auth
- SQL execution against hosted PostgreSQL
- Displaying SQL query results
- Saving SQL answers
- Retrieving saved answers after signing out and back in
- Displaying conceptual hints
- Displaying reference SQL solutions
- Executing reference queries to display expected output rows
- Successful GitHub Actions execution
- Deployment to Streamlit Community Cloud

The dedicated grader account provides a way to verify these features without requiring account registration.

Additional multi-user testing and security review would be appropriate before unrestricted public use.

### 5.9 Limitations

The application was developed as an educational SQL quiz rather than a production-grade SQL execution platform.

Current limitations include:

- Saved SQL answers are not automatically graded.
- The reviews table contains a sample of 10,000 reviews.
- Expected results are generated from the current database.
- Read-only permissions and SQL validation do not provide complete isolation for arbitrary SQL execution.

### 5.10 Future Improvements

Potential improvements include:

- Automated grading based on result-set equivalence
- Additional SQL questions and difficulty levels
- Student progress tracking
- Instructor-facing analytics
- Larger product and review datasets
- Stronger SQL execution isolation
- Query execution audit logging

### 5.11 Data Source

Kaggle: Sephora Products and Skincare Reviews dataset.

The data is used for educational SQL practice and analysis.

---
