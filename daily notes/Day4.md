# Day 4 — ABTalks Databricks Cohort

## Overview

Day 4 shifted from learning DataFrame APIs to building our own dataset. We generated a realistic synthetic healthcare-claims dataset using the `faker` library, injected intentional data quality issues (duplicates, nulls, mixed-case states, bad dates, implausible ages), and wrote everything as CSV files into the Unity Catalog raw volume. We also created two documentation files — a data dictionary and a medallion architecture plan — to guide the upcoming bronze-to-gold pipeline.

## What We Did

### 1. Installed faker and Set Up the Generator

- Added a `%pip install faker` cell before the main code cell — `faker` is not pre-installed on serverless compute.
- Seeded both `Faker` and `random` with `42` for reproducible synthetic data.
- Configured five entities: plans (20), providers (800), members (5,000), claims (50,000), and claim lines (1–8 per claim).

### 2. Generated Five Entities

- **Plans** — 20 insurance products with product types (HMO, PPO, EPO, POS, HDHP), metal levels (Bronze–Catastrophic), deductibles, copays, coinsurance, OOP max, and premiums.
- **Providers** — 800 healthcare providers with NPI, specialty, practice name, address, and network status. 5 duplicate rows injected (same `provider_id`, different name).
- **Members** — 5,000 insured members with demographics, DOB, age, plan enrollment. 10 duplicate rows injected (same `member_id`, different email/phone).
- **Claims** — 50,000 claims linked to members, providers, and plans. 15 duplicate rows injected. Claims carry billed/allowed/paid amounts, status, diagnosis codes, and denial reasons.
- **Claim Lines** — ~224,000 individual service lines (1–8 per claim) with CPT procedure codes, modifiers, quantities, and line-level amounts. 20 duplicate rows injected.

### 3. Injected Data Quality Issues

To make the silver-layer cleaning exercises meaningful, we deliberately introduced:
- **Duplicate rows** — same primary key, slightly different attribute values (5 providers, 10 members, 15 claims, 20 claim lines)
- **Null values** — varying rates across columns (e.g., ~50% null provider phones, ~25% null member emails, ~20% null procedure codes)
- **Mixed-case states** — lowercased and capitalized state codes in providers and members
- **Future dates** — 50 members with future enrollment dates; claims with far-future service/submission dates
- **Far-past dates** — claims with service dates 30–50 years in the past
- **NaT dates** — ~100 claims with `pd.NaT` in date fields
- **Out-of-order dates** — 30 claims where `service_end_date` < `service_start_date`
- **Implausible ages** — 20 members with ages like -5, 150, 999, or 0
- **Null foreign keys** — ~5% null `plan_id` on members, ~5% null `member_id` and ~15% null `provider_id` on claims

### 4. Wrote CSVs to the Raw Landing Zone

- Wrote all single-file entities (plans, providers, members, claim_lines) as individual CSVs to `/Volumes/health_claims/bronze/raw/`.
- Split claims into **3 dated CSV files** by `service_start_date` thirds (e.g., `claims_20240101_to_20240901.csv`) to practice incremental loading with Auto Loader later.
- Verified the landing zone with `dbutils.fs.ls()` and `dbutils.fs.head()` to inspect file sizes and sample lines.

### 5. Created Project Documentation

- **`docs/data_dictionary.md`** — Column-level reference for all five entities, including type, description, and known data quality issues per column. Includes an entity relationship diagram and a summary table of all injected issues.
- **`docs/medallion_plan.md`** — The raw → bronze → silver → gold pipeline plan: bronze ingestion strategy (COPY INTO for single files, Auto Loader for claims), silver cleaning steps (deduplication, standardization, date fixing, quarantine tables), and gold star schema (dimension + fact tables, aggregate tables for analytics).

### 6. Fixed a Syntax Error

- The f-string `f'{9920{0+i%5}'` on line 26 caused a `SyntaxError` — Python cannot parse nested curly braces inside an f-string expression delimiter.
- Fixed to `f'9920{i%5}'` where `9920` is literal text and `{i%5}` is the evaluated expression, producing CPT codes `99200`–`99204`.

## Key Takeaways

- **Synthetic data generation** with `faker` lets us build realistic datasets with controlled quality issues — perfect for practicing data engineering pipelines without needing real PII.
- **UC Volumes** (`/Volumes/health_claims/bronze/raw/`) serve as the raw landing zone for file-based data before ingestion into Delta tables.
- **Intentional data quality issues** (duplicates, nulls, bad dates, mixed-case states) make the bronze → silver cleaning layer meaningful and educational.
- **Documentation first** — writing the data dictionary and medallion plan before building the pipeline clarifies the schema, relationships, and transformation steps upfront.
- **f-string syntax**: curly braces inside f-string expressions must be valid Python expressions — `f'literal{expr}'` works, but `f'{literal{expr}}'` does not.

## Files Created

| File | Description |
| --- | --- |
| `notebooks/day04_generate_claims` | Synthetic data generation notebook |
| `docs/data_dictionary.md` | Column-level data dictionary for all 5 entities |
| `docs/medallion_plan.md` | Raw → Bronze → Silver → Gold architecture plan |
| `/Volumes/health_claims/bronze/raw/*.csv` | 7 CSV files (plans, providers, members, 3 claims, claim_lines) |

---
*Day 4 complete — synthetic healthcare claims generated, documented, and landed in the raw volume!* 🏥