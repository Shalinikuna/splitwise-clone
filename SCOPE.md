# SCOPE.md — Anomaly Log & Database Schema

## Overview

This document covers every data problem found in `Expenses_Export.csv`, how each was handled, and the final database schema used to store clean data.

---

## CSV Anomalies Found & How Each Was Handled

### DUPLICATE — Exact Duplicate Rows

| Row | Description | Action |
|-----|-------------|--------|
| Row 5 | `dinner - marina bites` on 08-02, ₹3200 — exact same date, description, and amount as Row 4 | **Skipped**. Fingerprint check (date + normalised description + amount) caught it. First occurrence imported, second skipped. |

**Detection logic:** A fingerprint `(date, normalised_description, amount_inr)` is stored for every imported row. If a new row matches an existing fingerprint exactly, it is skipped with code `DUPLICATE`.

---

### LIKELY_DUPLICATE — Fuzzy Duplicate (Same date + amount, similar description)

| Row | Description | Action |
|-----|-------------|--------|
| Rows 23–24 | Two Thalassa dinner entries on the same night. Rohan's note says Aisha's entry is wrong. | **Flagged** as `LIKELY_DUPLICATE`. Both imported — reviewer must decide which to keep. Row note preserved. |

**Detection logic:** If two rows share the same date and amount, and one description is a substring of the other, a `LIKELY_DUPLICATE` warning is added but the row is still imported.

---

### DATE_FORMAT — Non-standard Date Format

| Row | Raw Value | Action |
|-----|-----------|--------|
| Row 26 | `Mar-14` (no year) | Parsed using `%b-%d` format; year **assumed 2026**. Warning added. |
| Row 33 | `04-05-2026` noted as ambiguous (Apr 5 or May 4?) | Treated as `dd-mm-YYYY` → 4th May 2026. Warning `DATE_AMBIGUOUS` added. |

**Supported date formats tried in order:** `dd-mm-YYYY`, `dd-mm-YY`, `YYYY-mm-dd`, `Mon-dd`, `Month-dd`.

---

### MISSING_PAID_BY — No Payer

| Row | Description | Action |
|-----|-------------|--------|
| Row 22 | `paid_by` column is empty | **Skipped**. Cannot create a valid expense without a payer. Error logged. |

---

### AMOUNT_COMMA — Comma in Amount Field

| Row | Raw Value | Action |
|-----|-----------|--------|
| Row 10 | `"1,200"` | Stripped quotes and comma → `1200`. Info anomaly logged. |

---

### NEGATIVE_AMOUNT — Negative Value (Refund/Credit)

| Row | Raw Value | Action |
|-----|-----------|--------|
| Row 25 | `-30 USD` | Imported with `is_refund=True` flag. Amount stored as negative. Warning logged. |

---

### ZERO_AMOUNT — Zero Expense

| Row | Description | Action |
|-----|-------------|--------|
| Row 30 | Amount = 0 | **Skipped**. Zero-amount rows have no financial meaning. Warning logged. |

---

### FOREIGN_CURRENCY — USD Amounts

| Rows | Description | Action |
|------|-------------|--------|
| Rows 19, 20, 21 | Amounts in USD (`540 USD`, `84 USD`, `150 USD`) | Converted to INR at fixed rate **₹84/USD** (no live FX in scope). Original amount and currency stored. Info anomaly logged. |

**Trade-off:** A fixed rate is used because live FX lookup is out of scope for this MVP. Rate is defined as a constant in `engine.py` so it can be updated easily.

---

### MISSING_CURRENCY — Empty Currency Field

| Row | Description | Action |
|-----|-------------|--------|
| Row 27 | Currency field blank | **Defaulted to INR**. Warning logged. |

---

### NAME_NORMALISED — Inconsistent Member Names

| Raw Value | Canonical Name | Action |
|-----------|---------------|--------|
| `priya` | `Priya` | Normalised via `NAME_ALIASES` map |
| `Priya S` | `Priya` | Normalised, warning logged |
| `rohan ` (trailing space) | `Rohan` | Stripped and normalised |

All normalisation is done via a `NAME_ALIASES` dictionary in `engine.py`. The canonical member set is `{Aisha, Rohan, Priya, Meera, Dev, Sam}`.

---

### MEMBER_ISSUE — Non-Member in Split

| Row | Raw Value | Action |
|-----|-----------|--------|
| Row 21 | `Dev's friend Kabir` in `split_with` | `Kabir` is not a known member. **Excluded from split**. Warning logged. |

---

### STALE_MEMBER — Member Who Left Group

| Rows | Description | Action |
|------|-------------|--------|
| Rows 35–36 | `Meera` appears in `split_with` for April expenses; she moved out on 28-Mar-2026 | **Removed from split** for any expense dated April 1, 2026 or later. Warning `STALE_MEMBER` logged. |

---

### IS_SETTLEMENT — Row is a Settlement, Not an Expense

| Row | Description | Action |
|-----|-------------|--------|
| Row 25 | Note says "this is a settlement not an expense" / description contains "paid back" | **Moved to `ImportedSettlement` table**. Not added to expenses. Info anomaly logged. |

**Detection:** Keywords `paid back`, `settlement`, `deposit share` in description or notes trigger settlement classification.

---

### SPLIT_TYPE_CONFLICT — Equal Split but Weights Given

| Row | Description | Action |
|-----|-------------|--------|
| Row 41 | `split_type=equal` but `split_details` has share weights | **Overridden to `shares`** split type. Warning logged. The detailed weights are more specific than "equal" so they take precedence. |

---

### PCT_SUM_INVALID — Percentages Don't Add to 100%

| Row | Description | Action |
|-----|-------------|--------|
| Row 29 | Percentages: 30+30+30+20 = 110% | **Normalised proportionally**: each percentage divided by total (110) × 100. Warning logged with original values. |

---

### INVALID_SPLIT_TYPE — Unrecognised Split Type

| Row | Raw Value | Action |
|-----|-----------|--------|
| Any | Value not in `{equal, unequal, percentage, share, shares}` | **Defaulted to `equal`**. Warning logged. `share` is also normalised to `shares`. |

---

## Anomaly Code Reference

| Code | Severity | Meaning |
|------|----------|---------|
| `DUPLICATE` | error | Exact fingerprint match — row skipped |
| `LIKELY_DUPLICATE` | warning | Same date+amount, similar description |
| `DATE_FORMAT` | warning | Non-standard date — parsed with assumed year |
| `DATE_AMBIGUOUS` | warning | dd-mm vs mm-dd ambiguity noted |
| `DATE_INVALID` | error | Cannot parse date — row skipped |
| `MISSING_PAID_BY` | error | No payer — row skipped |
| `AMOUNT_COMMA` | info | Comma removed from amount |
| `AMOUNT_INVALID` | error | Cannot parse amount — row skipped |
| `NEGATIVE_AMOUNT` | warning | Stored as refund |
| `ZERO_AMOUNT` | warning | Skipped |
| `FOREIGN_CURRENCY` | info | Converted at fixed rate |
| `MISSING_CURRENCY` | warning | Defaulted to INR |
| `NAME_NORMALISED` | warning | Alias mapped to canonical name |
| `MEMBER_ISSUE` | warning | Non-member excluded from split |
| `STALE_MEMBER` | warning | Removed from post-March splits |
| `IS_SETTLEMENT` | info | Moved to settlements table |
| `SPLIT_TYPE_CONFLICT` | warning | Type overridden to match details |
| `PCT_SUM_INVALID` | warning | Percentages normalised to 100% |
| `INVALID_SPLIT_TYPE` | warning | Defaulted to equal |
| `UNEQUAL_SUM_MISMATCH` | warning | Split amounts ≠ expense total |
| `SPLIT_DETAIL_PARSE_ERROR` | warning | Could not parse split_details |

---

## Database Schema

### `importer_importsession`
```
id              UUID  PK
imported_by     FK → auth_app_user (nullable)
filename        VARCHAR(255)
status          ENUM('pending','complete','failed')
total_rows      INTEGER
imported_rows   INTEGER
skipped_rows    INTEGER
anomaly_count   INTEGER
created_at      TIMESTAMP
```

### `importer_importanomaly`
```
id              UUID  PK
session         FK → importer_importsession
row_number      INTEGER
code            VARCHAR(50)       -- e.g. DUPLICATE, DATE_FORMAT
message         TEXT
severity        ENUM('info','warning','error')
raw_description VARCHAR(500)
```

### `importer_importedexpense`
```
id                UUID  PK
session           FK → importer_importsession
row_number        INTEGER
date              DATE
description       VARCHAR(500)
paid_by           VARCHAR(100)     -- canonical name
amount_original   DECIMAL(12,2)   -- original CSV value
currency_original VARCHAR(10)     -- INR, USD etc.
amount_inr        DECIMAL(12,2)   -- converted to INR
split_type        VARCHAR(20)
split_with        JSONB            -- list of canonical names
split_details     JSONB            -- {name: amount/pct/shares}
notes             TEXT
is_refund         BOOLEAN
has_anomaly       BOOLEAN
```

### `importer_importedsettlement`
```
id          UUID  PK
session     FK → importer_importsession
row_number  INTEGER
date        DATE
description VARCHAR(500)
paid_by     VARCHAR(100)
paid_to     VARCHAR(100)
amount_inr  DECIMAL(12,2)
notes       TEXT
```

### Existing Splitwise Core Tables (unchanged)
See `AI_CONTEXT.md §5` for the full schema covering `users`, `groups`, `group_members`, `expenses`, `expense_splits`, `settlements`, `expense_comments`.
