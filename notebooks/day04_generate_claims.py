# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# dependencies = [
#   "faker",
# ]
# ///
# DBTITLE 1,Install faker
# MAGIC %pip install faker

# COMMAND ----------

import random
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
from faker import Faker

fake = Faker('en_US')
Faker.seed(42)
random.seed(42)

# ---------- Configuration ----------
N_MEMBERS   = 5_000
N_PLANS     = 20
N_PROVIDERS = 800
N_CLAIMS    = 50_000    # will be distributed across members
MIN_LINES_PER_CLAIM = 1
MAX_LINES_PER_CLAIM = 8

# ---------- Reference data ----------
PRODUCT_TYPES  = ['HMO', 'PPO', 'EPO', 'POS', 'HDHP']
METAL_LEVELS   = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Catastrophic']
NETWORK_STATUS = ['In-Network', 'Out-of-Network']
CLAIM_STATUSES = ['Approved', 'Denied', 'Partially Approved', 'Pending']
DENY_REASONS   = [None, 'Not Medically Necessary', 'Coverage Limit Exceeded',
                   'Missing Information', 'Duplicate Claim', 'Out of Network']
PROC_CODES     = [f'9920{i%5}' for i in range(5)] + \
                  [f'{cpt}' for cpt in ['85025', '71020', '36415', '93010', '80053',
                                        '45378', '44970', '29881', '73610', '70450']]
DIAG_CODES     = ['E11.9', 'I10', 'J06.9', 'M54.5', 'K21.9', 'N39.0',
                  'R51', 'Z00.00', 'E78.5', 'F41.1', 'J45.909', 'M25.561']
PROC_MODIFIERS = [None, '-25', '-59', '-TC', '-26', '-LT', '-RT']
PLACE_OF_SERVICE = ['Office', 'Hospital Outpatient', 'Emergency Room',
                    'Urgent Care', 'Inpatient', 'Telehealth']

# ---------- 1. Plans ----------
plans = []
for i in range(1, N_PLANS + 1):
    product = random.choice(PRODUCT_TYPES)
    metal   = random.choice(METAL_LEVELS)
    plans.append({
        'plan_id'            : f'PLN-{i:04d}',
        'plan_name'          : f'{metal} {product} {random.choice(["Premier","Essential","Basic","Plus","Value"])}',
        'product_type'       : product,
        'metal_level'        : metal,
        'deductible'         : round(random.choice([0, 500, 1000, 1500, 2500, 5000]), 2),
        'copay'              : round(random.choice([0, 10, 20, 30, 40, 50, 75]), 2),
        'coinsurance'        : random.choice([0, 10, 20, 30]),
        'oop_max'            : round(random.choice([1500, 3000, 5000, 7500, 10000]), 2),
        'monthly_premium'    : round(random.uniform(200, 1200), 2),
        'effective_date'     : fake.date_between(start_date='-5y', end_date='-1y'),
        'termination_date'   : random.choice([None, fake.date_between(start_date='-1y', end_date='today')]),
    })
df_plans = pd.DataFrame(plans)

# ---------- 2. Providers ----------
provider_types = ['Primary Care Physician', 'Cardiologist', 'Dermatologist',
                  'Orthopedic Surgeon', 'Radiologist', 'Emergency Medicine',
                  'Pediatrician', 'Oncologist', 'Psychiatrist', 'Anesthesiologist',
                  'General Practitioner', 'Neurologist']
specialty_map = {t: t for t in provider_types}

providers = []
for i in range(1, N_PROVIDERS + 1):
    providers.append({
        'provider_id'   : f'PRV-{i:05d}',
        'npi'           : fake.numerify('##########'),
        'provider_name' : fake.name(),
        'specialty'     : random.choice(provider_types),
        'practice_name' : fake.company() + ' Medical Group',
        'address'       : fake.street_address(),
        'city'          : fake.city(),
        'state'         : fake.state_abbr(),
        'zip_code'       : fake.zipcode(),
        'phone'         : fake.phone_number(),
        'network_status': random.choices(NETWORK_STATUS, weights=[0.8, 0.2])[0],
    })

# Inject a few duplicate providers (same provider_id, slightly different data)
for dup in random.sample(providers, 5):
    dup_copy = dict(dup)
    dup_copy['provider_name'] = fake.name()  # change name so it's not byte-identical
    providers.append(dup_copy)

# Sprinkle nulls and mixed-case states into providers
for p in random.sample(providers, 40):
    if random.random() < 0.5:
        p['phone'] = None
    if random.random() < 0.3:
        p['state'] = p['state'].lower()
    if random.random() < 0.2:
        p['npi'] = None
    if random.random() < 0.1:
        p['specialty'] = None

df_providers = pd.DataFrame(providers)

# ---------- 3. Members ----------
members = []
for i in range(1, N_MEMBERS + 1):
    dob     = fake.date_of_birth(minimum_age=0, maximum_age=90)
    members.append({
        'member_id'     : f'MBR-{i:06d}',
        'plan_id'       : random.choice(plans)['plan_id'],
        'subscriber_id' : f'SUB-{random.randint(100000, 999999)}',
        'first_name'    : fake.first_name(),
        'last_name'     : fake.last_name(),
        'gender'        : random.choice(['M', 'F']),
        'dob'           : dob,
        'age'           : (datetime.today().date() - dob).days // 365,
        'address'       : fake.street_address(),
        'city'          : fake.city(),
        'state'         : fake.state_abbr(),
        'zip_code'       : fake.zipcode(),
        'phone'         : fake.phone_number(),
        'email'         : fake.email(),
        'enrollment_date': fake.date_between(start_date='-5y', end_date='today'),
    })

# Inject a few duplicate members (same member_id, different email/phone)
for dup in random.sample(members, 10):
    dup_copy = dict(dup)
    dup_copy['email'] = fake.email()
    dup_copy['phone'] = fake.phone_number()
    members.append(dup_copy)

# Sprinkle nulls, mixed-case states, and bad dates into members
for m in random.sample(members, 300):
    r = random.random()
    if r < 0.25:
        m['email'] = None
    elif r < 0.40:
        m['phone'] = None
    elif r < 0.50:
        m['address'] = None
    if random.random() < 0.35:
        m['state'] = m['state'].lower()
    if random.random() < 0.15:
        m['state'] = m['state'].capitalize()
    if random.random() < 0.05:
        m['plan_id'] = None
    if random.random() < 0.03:
        m['dob'] = None
    if random.random() < 0.02:
        m['age'] = None

# Bad dates: future enrollment dates and impossible ages
for m in random.sample(members, 50):
    m['enrollment_date'] = fake.date_between(start_date='+1d', end_date='+2y')  # future date
for m in random.sample(members, 20):
    m['age'] = random.choice([-5, 150, 999, 0])  # implausible ages

df_members = pd.DataFrame(members)

# ---------- 4. Claims ----------
claims = []
for i in range(1, N_CLAIMS + 1):
    member   = random.choice(members)
    provider = random.choice(providers)
    service_date = fake.date_between(start_date='-2y', end_date='today')
    submitted_date = service_date + timedelta(days=random.randint(1, 14))
    status = random.choices(CLAIM_STATUSES, weights=[0.65, 0.15, 0.12, 0.08])[0]
    total_billed = round(random.uniform(50, 25000), 2)
    if status == 'Approved':
        total_paid = total_billed
        deny_reason = None
    elif status == 'Partially Approved':
        total_paid = round(total_billed * random.uniform(0.3, 0.8), 2)
        deny_reason = None
    elif status == 'Denied':
        total_paid = 0.0
        deny_reason = random.choice([r for r in DENY_REASONS if r])
    else:  # Pending
        total_paid = 0.0
        deny_reason = None
    claims.append({
        'claim_id'          : f'CLM-{i:07d}',
        'member_id'         : member['member_id'],
        'plan_id'           : member['plan_id'],
        'provider_id'       : provider['provider_id'],
        'claim_type'        : random.choice(['Medical', 'Pharmacy', 'Behavioral', 'Preventive']),
        'status'            : status,
        'service_start_date': service_date,
        'service_end_date'  : service_date + timedelta(days=random.randint(0, 5)),
        'submission_date'   : submitted_date,
        'total_billed'      : total_billed,
        'total_allowed'     : round(total_billed * random.uniform(0.4, 0.9), 2),
        'total_paid'        : total_paid,
        'member_responsibility': round(total_billed * random.uniform(0.05, 0.3), 2),
        'place_of_service'  : random.choice(PLACE_OF_SERVICE),
        'primary_diagnosis' : random.choice(DIAG_CODES),
        'denial_reason'     : deny_reason,
    })

# Inject a few duplicate claims (same claim_id, different totals)
for dup in random.sample(claims, 15):
    dup_copy = dict(dup)
    dup_copy['total_billed'] = round(random.uniform(50, 25000), 2)
    dup_copy['total_paid']  = round(dup_copy['total_billed'] * 0.7, 2)
    claims.append(dup_copy)

# Sprinkle nulls and bad dates into claims
for c in random.sample(claims, 500):
    r = random.random()
    if r < 0.15:
        c['provider_id'] = None
    elif r < 0.25:
        c['primary_diagnosis'] = None
    elif r < 0.30:
        c['place_of_service'] = None
    if random.random() < 0.05:
        c['member_id'] = None
    if random.random() < 0.03:
        c['total_billed'] = None

def make_bad_date():
    """Return a bad date value: NaT, far future, far past, or a string."""
    return random.choice([
        pd.NaT,
        fake.date_between(start_date='+1y', end_date='+5y'),   # future
        fake.date_between(start_date='-50y', end_date='-30y'),   # implausibly old
    ])

for c in random.sample(claims, 100):
    if random.random() < 0.5:
        c['service_start_date'] = make_bad_date()
    else:
        c['submission_date'] = make_bad_date()

# Bad ordering: service_end_date before service_start_date
for c in random.sample(claims, 30):
    c['service_end_date'] = c['service_start_date'] - timedelta(days=random.randint(1, 10))

df_claims = pd.DataFrame(claims)

# ---------- 5. Claim Lines ----------
claim_lines = []
line_num = 1
for claim in claims:
    n_lines = random.randint(MIN_LINES_PER_CLAIM, MAX_LINES_PER_CLAIM)
    for ln in range(1, n_lines + 1):
        billed = round(random.uniform(25, 5000), 2)
        allowed = round(billed * random.uniform(0.4, 0.9), 2)
        paid = allowed if claim['status'] in ('Approved', 'Partially Approved') else round(allowed * random.uniform(0, 0.6), 2)
        claim_lines.append({
            'claim_line_id'   : f'CLL-{line_num:08d}',
            'claim_id'        : claim['claim_id'],
            'line_number'     : ln,
            'procedure_code'  : random.choice(PROC_CODES),
            'procedure_mod'   : random.choice(PROC_MODIFIERS),
            'diagnosis_code'  : random.choice(DIAG_CODES),
            'quantity'         : random.choice([1, 1, 1, 2, 4]),
            'billed_amount'   : billed,
            'allowed_amount'  : allowed,
            'paid_amount'     : round(paid, 2),
            'member_responsibility': round(billed - allowed, 2),
            'service_date'    : claim['service_start_date'] + timedelta(days=random.randint(0, 3)),
            'network_status'  : random.choices(NETWORK_STATUS, weights=[0.8, 0.2])[0],
            'denial_reason'   : claim['denial_reason'] if claim['status'] == 'Denied' else None,
        })
        line_num += 1

# Inject a few duplicate claim lines (same claim_line_id, different amounts)
for dup in random.sample(claim_lines, 20):
    dup_copy = dict(dup)
    dup_copy['billed_amount'] = round(random.uniform(25, 5000), 2)
    dup_copy['paid_amount']   = round(dup_copy['billed_amount'] * 0.5, 2)
    claim_lines.append(dup_copy)

# Sprinkle nulls into claim lines
for cl in random.sample(claim_lines, 800):
    r = random.random()
    if r < 0.20:
        cl['procedure_code'] = None
    elif r < 0.35:
        cl['diagnosis_code'] = None
    elif r < 0.45:
        cl['network_status'] = None
    elif r < 0.50:
        cl['denial_reason'] = None
    if random.random() < 0.05:
        cl['paid_amount'] = None
    if random.random() < 0.03:
        cl['billed_amount'] = None

df_claim_lines = pd.DataFrame(claim_lines)

# ---------- Display summary ----------
print(f"plans:        {df_plans.shape}")
print(f"providers:    {df_providers.shape}")
print(f"members:      {df_members.shape}")
print(f"claims:       {df_claims.shape}")
print(f"claim_lines:  {df_claim_lines.shape}")

display(df_plans.head(5))
display(df_members.head(5))
display(df_providers.head(5))
display(df_claims.head(5))
display(df_claim_lines.head(10))

# ---------- Save raw files to /Volumes/health_claims/bronze/raw/ ----------
import os

RAW_DIR = '/Volumes/health_claims/bronze/raw'
os.makedirs(RAW_DIR, exist_ok=True)

def write_csv(df, filename):
    """Write a pandas DataFrame to a single CSV file in the raw directory."""
    path = os.path.join(RAW_DIR, filename)
    df.to_csv(path, index=False)
    print(f"  wrote {len(df):,} rows -> {path}")

# --- Plans, members, providers, claim_lines: one file each ---
print('Writing single-file datasets:')
write_csv(df_plans,       'plans.csv')
write_csv(df_providers,   'providers.csv')
write_csv(df_members,     'members.csv')
write_csv(df_claim_lines, 'claim_lines.csv')

# --- Claims: split into 3 dated files by service_start_date ---
print('\nSplitting claims into 3 dated files:')
df_claims_sorted = df_claims.sort_values('service_start_date', na_position='last').reset_index(drop=True)

# Use date-based boundaries: find the min/max service dates and split into thirds
valid_dates = pd.to_datetime(df_claims_sorted['service_start_date'], errors='coerce').dropna()
date_min, date_max = valid_dates.min(), valid_dates.max()
split1 = date_min + (date_max - date_min) / 3
split2 = date_min + 2 * (date_max - date_min) / 3

claims_part1 = df_claims_sorted[pd.to_datetime(df_claims_sorted['service_start_date'], errors='coerce') <= split1]
claims_part2 = df_claims_sorted[(pd.to_datetime(df_claims_sorted['service_start_date'], errors='coerce') > split1) & (pd.to_datetime(df_claims_sorted['service_start_date'], errors='coerce') <= split2)]
claims_part3 = df_claims_sorted[pd.to_datetime(df_claims_sorted['service_start_date'], errors='coerce') > split2]

# Attach date-range labels to filenames for traceability
file_date = datetime.today().strftime('%Y%m%d')
write_csv(claims_part1, f'claims_{date_min.strftime("%Y%m%d")}_to_{split1.strftime("%Y%m%d")}.csv')
write_csv(claims_part2, f'claims_{split1.strftime("%Y%m%d")}_to_{split2.strftime("%Y%m%d")}.csv')
write_csv(claims_part3, f'claims_{split2.strftime("%Y%m%d")}_to_{date_max.strftime("%Y%m%d")}.csv')

print('\nAll files written to', RAW_DIR)

# ---------- Verify the landing zone ----------
print('\n--- Landing zone listing ---')
for entry in dbutils.fs.ls(RAW_DIR):
    print(f'  {entry.size:>12,}  {entry.path}')

print('\n--- Sample lines from claims (first dated file) ---')
claims_files = [e.path for e in dbutils.fs.ls(RAW_DIR) if 'claims_' in e.name and e.name.endswith('.csv')]
if claims_files:
    sample_path = claims_files[0]
    print(f'  Reading from: {sample_path}')
    lines = dbutils.fs.head(sample_path, 2048).splitlines()
    for line in lines[:6]:
        print(f'    {line}')

print('\n--- Sample lines from members.csv ---')
members_path = RAW_DIR + '/members.csv'
lines_m = dbutils.fs.head(members_path, 2048).splitlines()
for line in lines_m[:6]:
    print(f'    {line}')