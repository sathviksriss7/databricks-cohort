# Day 1 — ABTalks Databricks Cohort

## Overview

Kicked off Day 1 of the ABTalks Databricks cohort! Today was all about getting comfortable with the Databricks platform and creating our first notebook.

## What We Did

### 1. Explored the Databricks Platform

- **Workspace Navigation**: Got familiar with the Databricks workspace layout — the sidebar, workspace browser, and catalog explorer.
- **Compute**: Learned about clusters and how to start, configure, and stop a compute resource.
- **Notebooks**: Understood the notebook interface — cells, execution, languages (Python, SQL, Scala, R), and how to switch between them.
- **Unity Catalog**: Brief overview of how data is governed through catalogs, schemas, and tables.

### 2. Created Our First Notebook

- Created a new notebook in the workspace.
- Ran a simple `print("Hello, Databricks!")` in a Python cell.
- Explored attaching the notebook to a running cluster.
- Learned how to execute cells and view results inline.

### 3. Tested Spark and SQL

- Used PySpark (`spark.range(10)`) to create a simple DataFrame and viewed results with `.show()`.
- Wrote basic SQL queries in a SQL cell (`SELECT * FROM range(10)`) to run directly against the Lakehouse.
- Compared PySpark DataFrame operations with equivalent SQL queries to understand both interfaces.
- Learned that Python and SQL cells can be mixed in the same notebook using `%sql` magic commands.

## Key Takeaways

- Databricks brings data engineering, analytics, and ML into one unified workspace.
- Notebooks support multiple languages and can be attached to clusters for interactive execution.
- Unity Catalog provides centralized governance for all data assets.
- Spark DataFrames and SQL are first-class citizens — both run on the same engine and can be combined in a single notebook.

## Next Steps

- Explore Delta Lake and table operations.
- Start working with data loading and transformations.
- Dive deeper into SQL and PySpark within notebooks.

---
*Day 1 complete — excited for what's next!* 🚀