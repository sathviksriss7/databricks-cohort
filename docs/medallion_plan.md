# Medallion Architecture Plan

Raw data flows through four layers: **Raw** (UC Volume landing zone) -> **Bronze** (raw Delta tables) -> **Silver** (cleaned, deduplicated, conformed) -> **Gold** (analytics-ready star schema and aggregates).

All tables live in the `health_claims` catalog. See [data_dictionary.md](data_dictionary.md) for column-level details and known data quality issues.

---

## Layer 0: Raw Landing Zone

**Location**: `/Volumes/health_claims/bronze/raw/`

CSV files written by `notebooks/day04_generate_claims`. No schema enforcement, no transformations.

| File(s) | Rows (approx) | Notes |
| --- | --- | --- |
| `plans.csv` | 20 | Single file |
| `providers.csv` | 805 | Single file; includes 5 duplicate rows |
| `members.csv` | 5,010 | Single file; includes 10 duplicate rows |
| `claims_YYYYMMDD_to_YYYYMMDD.csv` | ~16,700 each | 3 files split by `service_start_date` into thirds |
| `claim_lines.csv` | ~200,000 | Single file; 1-8 lines per claim |

---

## Layer 1: Bronze (`health_claims.bronze`)

**Goal**: Land raw CSVs into Delta tables with minimal transformation. Preserve every row as-is, including duplicates and bad data. Add load metadata only.

### Tables

| Table | Source File(s) | Primary Key (logical) |
| --- | --- | --- |
| `bronze.plans` | `plans.csv` | `plan_id` |
| `bronze.providers` | `providers.csv` | `provider_id` |
| `bronze.members` | `members.csv` | `member_id` |
| `bronze.claims` | `claims_*.csv` (3 files) | `claim_id` |
| `bronze.claim_lines` | `claim_lines.csv` | `claim_line_id` |

### Ingestion Strategy

- **Single-file entities** (plans, providers, members, claim_lines): Use `COPY INTO` for a one-shot bulk load. For re-runnable pipelines, switch to Auto Loader with `cloudFiles` mode.
- **Multi-file entity** (claims): Use Auto Loader (`cloudFiles.format = 'csv'`) to incrementally ingest all `claims_*.csv` files in the raw volume. This exercises incremental loading patterns.

### Bronze Columns Added

| Column | Type | Description |
| --- | --- | --- |
| `_ingest_date` | timestamp | When the row was loaded into bronze |
| `_source_file` | string | Original CSV file name the row came from |

### What Bronze Does NOT Do

- No deduplication (duplicates are preserved)
- No null handling (nulls pass through)
- No type casting beyond what Delta schema inference provides
- No filtering of bad dates or implausible ages

---

## Layer 2: Silver (`health_claims.silver`)

**Goal**: Clean, deduplicate, standardize, and enforce referential integrity. Silver is the trusted, conformed layer that downstream analytics and ML can rely on.

### Tables

| Table | Source | Key |
| --- | --- | --- |
| `silver.plans` | `bronze.plans` | `plan_id` (deduplicated) |
| `silver.providers` | `bronze.providers` | `provider_id` (deduplicated) |
| `silver.members` | `bronze.members` | `member_id` (deduplicated) |
| `silver.claims` | `bronze.claims` | `claim_id` (deduplicated) |
| `silver.claim_lines` | `bronze.claim_lines` | `claim_line_id` (deduplicated) |

### Cleaning Steps (per entity)

#### All Entities
1. **Deduplicate** on primary key, keeping the first occurrence (or latest by `_ingest_date`).
2. **Type cast** all columns to their proper types (date, decimal, integer, string).
3. **Add** `_updated_date` timestamp.

#### Providers & Members
4. **Standardize `state`**: `UPPER(state)` to normalize mixed-case codes.
5. **Flag** rows with null `npi` / `phone` / `email` rather than dropping them (keep `_has_null_npi` boolean for traceability).

#### Members
6. **Fix implausible `age`**: Recalculate from `dob` where possible; flag rows where `age` is null or out of range (0-120).
7. **Flag future `enrollment_date`**: Set `_enrollment_date_flag = 'future'` where `enrollment_date > current_date()`.

#### Claims
8. **Flag bad dates**: `_date_flag` column marking rows with `NaT`, far-future, or far-past `service_start_date` or `submission_date`.
9. **Fix out-of-order dates**: Where `service_end_date < service_start_date`, set `service_end_date = service_start_date` and flag with `_date_order_fixed = true`.
10. **Flag null FKs**: `_has_null_member_id`, `_has_null_provider_id` booleans.

#### Claim Lines
11. **Inherit** parent claim status via join to `silver.claims` for validation.
12. **Flag** rows with null `procedure_code` or `diagnosis_code`.

### Quarantine Tables (optional)

Rows that fail critical quality checks can be routed to quarantine tables for manual review:

- `silver.quarantine_members` - rows with null `dob` and unfixable `age`, or future enrollment dates
- `silver.quarantine_claims` - rows with `NaT` service dates, null `member_id`, or null `provider_id`
- `silver.quarantine_claim_lines` - rows with null `procedure_code` AND null `diagnosis_code`

---

## Layer 3: Gold (`health_claims.gold`)

**Goal**: Analytics-ready star schema and aggregate tables for dashboards, reporting, and ML feature engineering.

### Star Schema

#### Dimension Tables

| Table | Source | Key | Description |
| --- | --- | --- | --- |
| `gold.dim_plans` | `silver.plans` | `plan_id` (surrogate: `plan_sk`) | Plan attributes (type, metal, cost-sharing) |
| `gold.dim_members` | `silver.members` | `member_id` (surrogate: `member_sk`) | Member demographics (age, gender, state) |
| `gold.dim_providers` | `silver.providers` | `provider_id` (surrogate: `provider_sk`) | Provider attributes (specialty, network status) |
| `gold.dim_date` | derived | `date_sk` | Calendar dimension from min to max service date |

#### Fact Tables

| Table | Source | Key | Grain | Description |
| --- | --- | --- | --- | --- |
| `gold.fact_claims` | `silver.claims` | `claim_id` | One row per claim | Claim-level metrics with FKs to dim tables |
| `gold.fact_claim_lines` | `silver.claim_lines` | `claim_line_id` | One row per claim line | Line-level metrics with FKs to dim tables and fact_claims |

### Aggregate Tables

| Table | Grain | Key Metrics |
| --- | --- | --- |
| `gold.claims_summary_by_month` | Year, month | `total_claims`, `total_billed`, `total_paid`, `denial_rate` |
| `gold.claims_by_provider` | `provider_id` | `claim_count`, `total_billed`, `total_paid`, `avg_claim_amount` |
| `gold.claims_by_member` | `member_id` | `claim_count`, `total_billed`, `total_paid`, `total_member_responsibility` |
| `gold.denial_analysis` | `denial_reason`, `claim_type` | `denied_count`, `denial_rate`, `total_denied_amount` |
| `gold.provider_network_summary` | `network_status`, `specialty` | `claim_count`, `total_billed`, `total_paid` |

### Gold Fact Table Columns (fact_claims)

| Column | Type | Description |
| --- | --- | --- |
| `claim_id` | string | Original claim ID (business key) |
| `member_sk` | long | FK to `dim_members` |
| `plan_sk` | long | FK to `dim_plans` |
| `provider_sk` | long | FK to `dim_providers` (null if missing) |
| `date_sk` | int | FK to `dim_date` (from `service_start_date`) |
| `claim_type` | string | Medical / Pharmacy / Behavioral / Preventive |
| `status` | string | Approved / Denied / Partially Approved / Pending |
| `total_billed` | decimal | Sum of all line billed amounts |
| `total_allowed` | decimal | Sum of all line allowed amounts |
| `total_paid` | decimal | Sum of all line paid amounts |
| `member_responsibility` | decimal | Member out-of-pocket total |
| `denial_reason` | string | Null if not denied |

---

## Pipeline Flow Summary

```
Raw Volume (/Volumes/health_claims/bronze/raw/)
  |
  | COPY INTO / Auto Loader
  v
Bronze (health_claims.bronze)
  bronze.plans | bronze.providers | bronze.members | bronze.claims | bronze.claim_lines
  |
  | Deduplicate, standardize, type-cast, flag bad data
  v
Silver (health_claims.silver)
  silver.plans | silver.providers | silver.members | silver.claims | silver.claim_lines
  |
  | Build star schema + aggregates
  v
Gold (health_claims.gold)
  dim_plans | dim_members | dim_providers | dim_date
  fact_claims | fact_claim_lines
  claims_summary_by_month | claims_by_provider | claims_by_member | denial_analysis
```

---

## Implementation Order

1. **Day 4** (current): Generate raw data -> `day04_generate_claims` notebook writes CSVs to the raw volume.
2. **Day 5**: Bronze ingestion - `COPY INTO` for single-file entities, Auto Loader for claims.
3. **Day 6**: Silver cleaning - deduplication, standardization, data quality flagging.
4. **Day 7**: Gold analytics - star schema, aggregate tables, first dashboards.