# Data Dictionary

Reference for every column in the five generated entities. Data is produced by `notebooks/day04_generate_claims` and lands as CSV files in `/Volumes/health_claims/bronze/raw/`.

Intentional data quality issues (duplicates, nulls, mixed-case states, bad dates, implausible ages, out-of-order dates) are noted per column in the **Known Issues** column so the silver-layer cleaning steps can target them.

---

## 1. Plans (`plans.csv`)

20 rows. One row per insurance plan product.

| Column | Type | Description | Known Issues |
| --- | --- | --- | --- |
| `plan_id` | string (`PLN-NNNN`) | Primary key | None |
| `plan_name` | string | Human-readable name, e.g. "Gold PPO Premier" | None |
| `product_type` | string | `HMO`, `PPO`, `EPO`, `POS`, `HDHP` | None |
| `metal_level` | string | `Bronze`, `Silver`, `Gold`, `Platinum`, `Catastrophic` | None |
| `deductible` | decimal | Annual deductible in USD (0-5,000) | None |
| `copay` | decimal | Fixed copay in USD (0-75) | None |
| `coinsurance` | integer | Coinsurance percentage (0, 10, 20, 30) | None |
| `oop_max` | decimal | Out-of-pocket maximum in USD (1,500-10,000) | None |
| `monthly_premium` | decimal | Monthly premium in USD (200-1,200) | None |
| `effective_date` | date | Plan effective date (1-5 years ago) | None |
| `termination_date` | date or null | Termination date; `null` if plan is still active | None |

---

## 2. Providers (`providers.csv`)

805 rows (800 originals + 5 duplicate rows injected). One row per healthcare provider.

| Column | Type | Description | Known Issues |
| --- | --- | --- | --- |
| `provider_id` | string (`PRV-NNNNN`) | Intended primary key | 5 duplicate rows with same `provider_id` but different `provider_name` |
| `npi` | string (10 digits) | National Provider Identifier | ~2% null |
| `provider_name` | string | Provider full name | None |
| `specialty` | string | One of 12 specialties (PCP, Cardiologist, etc.) | ~1% null |
| `practice_name` | string | Practice / group name | None |
| `address` | string | Street address | None |
| `city` | string | City | None |
| `state` | string | 2-letter state code | ~30% lowercased, some mixed case |
| `zip_code` | string | ZIP code | None |
| `phone` | string | Phone number | ~50% null (injected subset) |
| `network_status` | string | `In-Network` or `Out-of-Network` (80/20 split) | None |

---

## 3. Members (`members.csv`)

5,010 rows (5,000 originals + 10 duplicate rows injected). One row per insured member.

| Column | Type | Description | Known Issues |
| --- | --- | --- | --- |
| `member_id` | string (`MBR-NNNNNN`) | Intended primary key | 10 duplicate rows with same `member_id` but different email/phone |
| `plan_id` | string (`PLN-NNNN`) | FK to plans.plan_id | ~5% null (orphaned members) |
| `subscriber_id` | string (`SUB-NNNNNN`) | Subscriber / policyholder ID | None |
| `first_name` | string | First name | None |
| `last_name` | string | Last name | None |
| `gender` | string | `M` or `F` | None |
| `dob` | date | Date of birth | ~3% null |
| `age` | integer | Age in years | ~2% null; 20 rows with implausible values (-5, 150, 999, 0) |
| `address` | string | Street address | ~10% null |
| `city` | string | City | None |
| `state` | string | 2-letter state code | ~35% lowercased, ~15% capitalized |
| `zip_code` | string | ZIP code | None |
| `phone` | string | Phone number | ~15% null |
| `email` | string | Email address | ~25% null |
| `enrollment_date` | date | Enrollment date | 50 rows have future dates (1 day to 2 years ahead) |

---

## 4. Claims (`claims_*.csv` - 3 dated files)

50,015 rows (50,000 originals + 15 duplicate rows injected). One row per insurance claim. Files are split by `service_start_date` into thirds for incremental-load practice.

| Column | Type | Description | Known Issues |
| --- | --- | --- | --- |
| `claim_id` | string (`CLM-NNNNNNN`) | Intended primary key | 15 duplicate rows with same `claim_id` but different totals |
| `member_id` | string (`MBR-NNNNNN`) | FK to members.member_id | ~5% null |
| `plan_id` | string (`PLN-NNNN`) | FK to plans.plan_id (inherited from member) | May be null if member's `plan_id` is null |
| `provider_id` | string (`PRV-NNNNN`) | FK to providers.provider_id | ~15% null |
| `claim_type` | string | `Medical`, `Pharmacy`, `Behavioral`, `Preventive` | None |
| `status` | string | `Approved` (65%), `Denied` (15%), `Partially Approved` (12%), `Pending` (8%) | None |
| `service_start_date` | date | First service date (~2 years ago to today) | Some `NaT`, far-future (+1 to +5 yr), far-past (-50 to -30 yr) |
| `service_end_date` | date | Last service date (start + 0-5 days) | 30 rows have end date before start date |
| `submission_date` | date | Submission date (service + 1-14 days) | Some `NaT`, far-future, far-past |
| `total_billed` | decimal | Total billed in USD (50-25,000) | ~3% null |
| `total_allowed` | decimal | Allowed amount (40-90% of billed) | None |
| `total_paid` | decimal | Paid amount: full billed if Approved; 30-80% if Partial; 0 if Denied/Pending | None |
| `member_responsibility` | decimal | Member out-of-pocket portion (5-30% of billed) | None |
| `place_of_service` | string | `Office`, `Hospital Outpatient`, `Emergency Room`, `Urgent Care`, `Inpatient`, `Telehealth` | ~5% null |
| `primary_diagnosis` | string | ICD-10 code (e.g. `E11.9`, `I10`) | ~10% null |
| `denial_reason` | string or null | Reason if Denied; null otherwise | Null for non-denied claims (by design) |

---

## 5. Claim Lines (`claim_lines.csv`)

Variable row count (1-8 lines per claim, ~200k total). One row per individual service line on a claim.

| Column | Type | Description | Known Issues |
| --- | --- | --- | --- |
| `claim_line_id` | string (`CLL-NNNNNNNN`) | Intended primary key | 20 duplicate rows with same `claim_line_id` but different amounts |
| `claim_id` | string (`CLM-NNNNNNN`) | FK to claims.claim_id | None |
| `line_number` | integer | Line number within the claim (1-8) | None |
| `procedure_code` | string | CPT code (e.g. `99201`, `85025`, `71020`) | ~20% null |
| `procedure_mod` | string or null | Modifier (`-25`, `-59`, `-TC`, `-26`, `-LT`, `-RT`, or null) | None (null is valid) |
| `diagnosis_code` | string | ICD-10 code | ~15% null |
| `quantity` | integer | Units of service (1, 2, or 4) | None |
| `billed_amount` | decimal | Billed amount per line (25-5,000) | ~3% null |
| `allowed_amount` | decimal | Allowed amount per line (40-90% of billed) | None |
| `paid_amount` | decimal | Paid amount: full allowed if Approved/Partial; 0-60% otherwise | ~5% null |
| `member_responsibility` | decimal | Member portion (billed - allowed) | None |
| `service_date` | date | Service date (claim start + 0-3 days) | Inherits bad dates from parent claim's `service_start_date` |
| `network_status` | string | `In-Network` or `Out-of-Network` (80/20 split) | ~10% null |
| `denial_reason` | string or null | Denial reason if parent claim is Denied; null otherwise | Some additional nulls injected (~10%) |

---

## Entity Relationship Summary

```
plans --< members --< claims --< claim_lines
                      |            |
                      |            +--> providers (via provider_id)
                      +--> plans (via plan_id)
```

- **plans** 1-N **members** (on `plan_id`)
- **members** 1-N **claims** (on `member_id`)
- **providers** 1-N **claims** (on `provider_id`)
- **claims** 1-N **claim_lines** (on `claim_id`)

---

## Injected Data Quality Issues - Summary

| Issue Type | Entities Affected | Scope |
| --- | --- | --- |
| Duplicate rows | providers (5), members (10), claims (15), claim_lines (20) | Same PK, slightly different attribute values |
| Null values | All entities | Various columns (see tables above) |
| Mixed-case states | providers, members | lowercased / capitalized state codes |
| Future dates | members (enrollment_date), claims (service_start_date, submission_date) | 1 day to 5 years ahead |
| Far-past dates | claims | 30-50 years before realistic range |
| NaT dates | claims | ~100 rows with `NaT` in date fields |
| Out-of-order dates | claims | 30 rows where `service_end_date` < `service_start_date` |
| Implausible ages | members | 20 rows with -5, 150, 999, or 0 |
| Null foreign keys | members (plan_id), claims (member_id, provider_id) | Orphaned referential integrity |