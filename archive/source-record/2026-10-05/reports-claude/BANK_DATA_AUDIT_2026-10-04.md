# Bank data audit for the dataset-mode sensor (2026-10-04)

Read-only audit of the REAL bank dataset (13 tables, `D:\.codex\factored\data`) and E0 (`pulso_muestra_e0\datos`, 9 operational tables; `labels` and `timeline` NOT used; `signal` used only as a row count, never as an input). Aggregates only. Every count printed here is >= 10 (smaller cells were suppressed as `<10`). No model calls, no network, no AWS, nothing under `D:\Nexus`, no repo touched. Row-level material lived only in a DuckDB file in the session scratchpad and was deleted at the end (see section 9).

Method in one line: DuckDB over the daily CSV partitions (all rows for the 7 fact tables except `digital_events`, which was stream-aggregated in full without materialising row-level output, plus a day-15-of-each-month sample for its profile), E0 through pyarrow/DuckDB. Row counts match the quality report (F4 there): complaints 67,095, contacts 686,296, surveys 212,759, transcripts 171,321, transactions 4,425,008, digital_events 15,620,994, campaign_sends 1,746,801.

## 0. Executive summary (what the data really supports)

1. The bank data is almost entirely STATIONARY and HOMOGENEOUS. Over 37 months every monthly series has binomial dispersion (chi2/df 0.6 to 1.1, trend p > 0.4); within a contact reason, nothing differentiates outcomes by channel, country, segment, agent, hour, weekday, month, sentiment-mix or customer history (agent dispersion chi2/df 0.97, p 0.93). Contacts per customer are Poisson (mean 4.575, variance 4.584); recontact is at the random rate. The ONLY real structure in contacts is the contact reason.
2. The one strong, recurring, replicating problem is unresolved contacts by reason: Queja 56.4% (66,000 / 117,021) vs 16.6% for all other reasons, +39.8 pp [39.5, 40.1]; same in every customer half, agent half, time window, channel and year, and in 37 of 37 months. Retencion 39.8%, Comercial 34.8% and Tecnico 30.1% are the next-worst; Producto 10.4% and Transaccional 8.5% are low.
3. Several "obvious" candidates are NON-findings or artifacts and must be reported as such: PQR SLA breach (flat 20.1% everywhere), PQR open backlog (the status does not depend on age), transaction declines (flat 5.0%), recontact, agent outliers, wait and escalation, followup (a deterministic superset of unresolved), CSAT (a function of the resolved flag), and `complaints.subcategory` (a 1:1 function of `category`).
4. Dates are usable at day/month granularity inside ONE table (constant naive offset to the partition, no DST shift in 3 years), not for sub-day ordering across tables and not as "as-of" views (final-extract outcomes). Temporal windows are therefore legitimate for descriptive recurrence, but there is nothing temporal to detect (no onset/drift anywhere), and the spec's `n_known >= 500` per 30-day cell is met only by Phone cells. Recommended primary replication: cross-sectional (customer-hash halves), secondary: two long time windows, tertiary: strata.
5. The bank tells WHERE (which reasons are unresolved), never WHY and never a contact -> complaint chain (`origin_interaction_id` 100% null; same-customer contact within 24 h of a PQR 0.42%, within 7 d 2.87% = the random expectation 2.87%). Concrete mechanisms come only from E0 (repeated copilot query).

## 1. Data capability map

Layout common to the 7 fact tables: one CSV per day, `year=YYYY/month=MM/day=DD/<table>_YYYYMMDD.csv`, 1,097 daily partitions (2023-06-17 .. 2026-06-17), same columns in every file (no schema evolution, 0 cast failures per the quality report). Dimensions (`customers`, `products`, `branches`, `service_agents`, `marketing_campaigns`, `daily_exchange_rates`) are single CSVs. All timestamps are NAIVE (no zone marker), second precision, hour-of-day uniform (see section 2).

### 1.1 Fact tables

| Table | Grain | Rows | Event column and range | Volume/month (full months) | Key columns (null %) |
|---|---|---|---|---|---|
| `call_center_interactions` | one contact | 686,296 (PK unique) | `interaction_date` 2023-06-17 08:03 .. 2026-06-18 07:58; 37 calendar months (35 full: 2023-07..2026-05) | ~19.0k (min 17.2k Feb-25, max 20.4k Mar-26); partial first month 9,012, last 11,143 | `reason_category` 0 (6 values), `contact_reason` 0 (IDENTICAL to category in 100% of rows), `channel` 0 (6), `interaction_type` 0 (5), `was_resolved` 0, `requires_followup` 0, `was_escalated` 0, `duration_seconds` 14.0 (structural: null for Chat and Email), `wait_time_seconds` 30.0 (structural: only Inbound Call), `detected_sentiment` 0, `sentiment_score` 0, `customer/agent_detected_accent` 29.8, `mentioned_products` 60.0, `has_transcript` 0 (25.0% true) |
| `complaints` (PQR) | one complaint | 67,095 (PK unique; 54,145 customers; 1,200 agents) | `creation_date` 2023-06-17 .. 2026-06-18; 37 months | ~1.87k (1,706 .. 2,001); partial 796 / 1,064 | `category` 0 (5), `subcategory` 9.98, `case_type` 0 (4), `reception_channel` 0 (6), `priority` 0 (4), `status` 0 (6), `sla_breached` 0, `affected_product_id` 33.6, `related_branch_id` 71.4, `origin_interaction_id` **100.0**, `assigned_agent_id` 34.5, `assignment_date` 34.5, `first_response_date` 39.1, `resolution_date` 77.1, `resolution_days` 77.1, `resolution` 77.2 (5 template sentences), `closing_date` 96.3, `compensation_granted` 93.1, `resolution_satisfaction` 96.3, `claimed_amount` 67.6, `currency` 67.5, `is_repeat_complainer` 0; free text `description` NOT read |
| `satisfaction_surveys` | one survey answer, 1:1 to an interaction | 212,759 (113,640 customers) | `survey_date` 2023-06-17 09:29 .. 2026-06-19 06:54 | ~5.9k | `survey_type` 0 (CSAT 60.1%, NPS 29.9%, CES 10.0%), `send_channel` 0 (5), `main_score` 0, `nps_category` 71.6, `question_1/2/3_response` 43.0/61.7/81.2, `comment_sentiment` 52.4, `response_time_hours` 0, `campaign_response_rate` 15.1; free text NOT read |
| `call_transcripts` | one transcript, 1:1 to an interaction | 171,321 (25.0% of contacts) | no event timestamp (partition only) | ~4.6k | `detected_language` 0 (es 100%), `detected_intents` 4.9 (ONE value `consulta_general` for every non-null), `main_topics` 0 (= the contact reason in 100%), `audio_quality` 5.0, `duration_seconds` 14.0; text NOT read. No semantic signal. |
| `transactions` | one transaction | 4,425,008 (134,515 customers, 339,963 products) | `transaction_date` 2023-06-17 06:01 .. 2026-06-18 05:59 | ~122k | `transaction_type` 0 (6), `transaction_category` 60.9, `amount_usd` 57.3, `channel` 0 (6), `branch_id` 68.6, `merchant_category` 76.8, `transaction_country` 0 (7, `Mexico`/`Mexico` spelling variants), `transaction_status` 0 (Approved 92.0, Declined 5.0, Pending 2.0, Reversed 1.0), `response_code` 5.0 (00 87.4; 05/14/51/54 about 1.9 each), `is_fraud` 0 (0.10% true), `fraud_score` 20.0 |
| `digital_events` | one app/web event | 15,620,994 (about 150k identified customers) | `event_date` 2023-06-17 06:02 .. 2026-06-18 06:04 | ~430k (371k .. 515k) | `event_type` 0 (7: PageView 38.2, Click 22.9, Login 15.7, Logout 15.6, FormSubmit 3.9, Error 2.3, Purchase 1.5), `channel` 0 (4), `platform` 5.0, `action` 10.0 (12 values), `app_version` 42.6 (about 600 distinct versions, fragmented), `customer_id` 23.7 (anonymous), `session_id` 0, `duration_seconds` 63.7 (structural), `event_value` 94.9, `utm_source` 94.6 |
| `campaign_sends` | one campaign send | 1,746,801 (150,000 customers, 175 campaigns) | `send_date` 2023-07-01 06:00 .. 2026-06-18 05:59; 36 months | ~48.5k | `send_channel` 0 (5), `send_status` 0 (Sent 94.0, Failed 3.0, Bounced 2.0, Blocked 1.0), `was_delivered` 0, `was_opened` 27.7 (null for Voice and WhatsApp), `was_clicked` 0, `had_conversion` 0 (0.56%), `failure_reason` 94.3, `send_cost` 15.0 |

### 1.2 Dimensions and reference tables

| Table | Rows | Columns of interest (null %) |
|---|---|---|
| `customers` | 150,000 | `country` (México 49.9, Colombia 30.2, Argentina 19.9; "México" accented), `segment` 0 (Basic 59.8, Plus 25.0, Premium 10.1, Student 5.0), `customer_status` 0 (Active 85.1, Inactive 9.9, Suspended 2.9, Closed 2.0), `accepts_marketing` 0 (50.0/50.0), `detected_accent` 29.9, `credit_score` 15.0, `estimated_monthly_income` 20.0, `registration_date` 2018-06 .. 2026-06, `registration_branch_id` 0 but 99.997% orphan; PII columns (names, document, email, phone, address, DOB) NOT read |
| `products` | 400,000 | `product_type` 8 (Cuenta Ahorro 30.1, Tarjeta Credito 25.0, Cuenta Corriente 25.0, Tarjeta Debito 10.0, Prestamo Personal 5.0, Hipotecario 3.0, Inversion 1.5, Seguro 0.5), `product_status` (Active 85.0, Closed 8.0, Blocked 5.0, Suspended 2.0), `days_past_due` 68.7 null (non-credit) and > 0 in 14.97% of credit/loan products (10.0% > 30 d), `credit_limit` 68.7, `opening_date` to 2026-06-17, `last_transaction_date` 23.6 |
| `branches` | 350 | `branch_type` 4, `country` (50/30/20%), `geographic_zone` 100% "Urbana", `branch_status` 96% Active |
| `service_agents` | 1,200 (1,090 Active) | `agent_type` (Phone 49.0, Digital 20.9, In-Person 19.2, Hybrid 10.9), `experience_level` (Specialist 63.4, Senior 23.8, Mid-Senior 11.3, Junior 1.5), `specialty` 39.7 null, `work_shift` 4, `avg_csat` 11.2 null, `assigned_branch_id` 30.6 null and 99.8% orphan |
| `marketing_campaigns` | 200 (175 used) | `campaign_type` 6, `campaign_objective` 5, `target_segment` 39.5 null, `target_country` 55.5 null, `budget` 15.5 null, `expected_conversion_rate` 7.0 null |
| `daily_exchange_rates` | 13,164 | not used in findings |

### 1.3 Categorical dimensions: closed vocabularies (proposed normalization, lower-case ASCII, accents folded)

- `reason_category` (= `contact_reason`): `transaccional` 35.0%, `producto` 22.0%, `queja` 17.1%, `tecnico` 15.0%, `comercial` 8.0%, `retencion` 3.0%. Reason count of unresolved: queja 66,000; tecnico 30,940; transaccional 20,385; comercial 19,093; producto 15,650; retencion 8,198.
- `channel` (contacts): `phone` 85.0% (Inbound Call 70.0%, Outbound Call 14.9%), `email` 4.0%, `app` 3.8% (chat 22,947 + video 3,417), `whatsapp` 3.3%, `web_chat` 3.3%, `web` 0.5% (all Video). Recommend keeping `web` (video) distinct from `web_chat`; the Codex doc maps non-empty unknown channels to `other`, here no unknown channels exist.
- `interaction_type`: Inbound Call, Outbound Call, Chat, Email, Video (consistent with channel: Chat is only App/Web Chat/WhatsApp, Video only App/Web).
- PQR `category`: Transactions 20.2%, Fees 20.2%, Technical 20.0%, Branch 19.9%, Service 19.7% (flat). `subcategory` is a 1:1 function of category plus a 10% null: Transactions -> "Cargo no reconocido", Fees -> "Cobro indebido", Technical -> "Problema con app", Branch -> "Atencion en sucursal", Service -> "Calidad de servicio". So the "Cobro indebido" topic of the star story is simply category Fees. `case_type`: Complaint 60.3, Claim 24.7, Request 10.1, Suggestion 4.9 (independent of category). `reception_channel`: Call Center 50.3, Email 19.9, Web 14.7, App 10.0, Branch 4.0, Regulator 1.07. `priority`: Medium 49.8, Low 30.4, High 14.7, Critical 5.0. `status`: In Process 40.0, Open 30.0, Resolved 20.1, Escalated 5.0, Closed 3.9, Rejected 1.1.
- Country: normalize `México`/`Mexico` to `mx` (transactions `transaction_country` and `ip_country` carry both spellings; customers carry only the accented one); `Colombia`, `Argentina`; foreign transaction countries USA, Spain, Brazil, Mexico (0.9% each, same decline rate as domestic).
- Segment (customers): basic, plus, premium, student. Survey type: csat, nps, ces. Event type (digital): 7 values above.

### 1.4 Outcome fields and their true semantics

| Field | What it is | Caveat |
|---|---|---|
| `was_resolved` (contacts) | final-extract flag, 76.65% true | no censoring visible: unresolved share in the last full months equals early months. Not as-of. |
| `requires_followup` | 34.83% true | = 100% of unresolved contacts (160,266 of 160,266) PLUS a constant 14.9-15.4% of resolved contacts for every reason. A superset of unresolved, not an independent outcome: do not count it twice. |
| `was_escalated` | 9.96% | flat (9.8-10.5%) across reason, channel, country, month, agent. |
| `wait_time_seconds` | only Inbound Call (480,678); median 119 s, p90 196, p99 259, max 424; > 300 s in 0.13% | flat by reason, month. No SLA threshold exists. |
| `duration_seconds` | null for Chat/Email; mean by reason: Comercial 540, Retencion 479, Queja 435, Tecnico 361, Producto 266, Transaccional 221 | depends on reason only (resolved vs unresolved equal except Transaccional +22%: 264.8 vs 216.7 s). |
| `detected_sentiment`, `sentiment_score` | Transaccional has zero negative sentiment and score 0; every other non-Producto reason has 34.9% negative; Producto 19.2% | sentiment is a function of reason (artifact of generation); within Producto it shifts unresolved 9.5% .. 12.4%. Treat as derived. |
| PQR `sla_breached` | 20.11% true, never null | statistically independent of every field including the timestamps (median first response 38 h breached vs 37 h not; resolution days 15 vs 16; > 48 h first response 20.6% vs <= 48 h 20.2%). A random provided flag, not a derived SLA. |
| PQR `status` | snapshot; Open/In Process/Escalated = 74.9% | independent of age: open-like 74.7% for complaints younger than 1 year, 74.9% for 1-2 y, 75.1% for 2-3 y (median age of open-like 547 d). Not a backlog dynamic. Open (30.0%) and Rejected (1.1%) have NO assigned agent, NO first response, NO resolution; Escalated has an agent but no response; In Process has agent and response; Resolved/Closed have a resolution in about 95% of rows. |
| PQR `resolution_date` | 22.9% present; 1.4% are after the extract end (up to 2026-07-18); 3.4% precede the first response | leakage hazard for any as-of view |
| PQR `resolution_satisfaction` | 3.7% present (1-5 uniform), only for Closed | flat vs resolution days |
| PQR `is_repeat_complainer` | 15.03% true | NOT derived from history: 15.1% among customers with exactly one PQR; customers with 2/3/4 PQRs flag at 27%/39%/51% only because a customer with k PQRs has k draws. Per-customer PQR counts are Poisson (mean 0.447). |
| `main_score` | CSAT and CES on a 1-4 scale, NPS on 2-7 (truncated); `nps_category` thresholds make 70% of NPS "detractors" | do not mix survey types in one mean or low-score rate. Score is a function of `was_resolved` (see F04). |
| Transactions `transaction_status` | Declined 5.0% flat; Declined carries response codes 05/14/51/54 uniformly (about 62% of each code is Declined, the rest Pending/Reversed); Approved carries `00` or null | no semantic structure |
| `had_conversion` | 0.56% | descriptive, not incremental |

### 1.5 Join keys and coverage

| Join | Coverage | Verdict |
|---|---|---|
| `complaints.origin_interaction_id` -> interactions | **100.0% null (67,095/67,095)** | CONFIRMED unusable. Proximity link also fails: same-customer contact in the 24 h before a PQR 0.42%; in the 7 d before 2.87% (random expectation 2.87%); after 2.92%; by reception channel Call Center 2.91%. Contacts and complaints are independent given the customer. PQR rate per customer does not depend on number of contacts (0.43 .. 0.47 flat over 0..12 contacts). |
| `satisfaction_surveys.interaction_id` -> interactions | 212,759/212,759 resolve; customer and agent agree 100%; survey exists for 31.0% of contacts | coverage is flat across reasons (30.9-31.3%) and channels (30.6-31.8%): no differential non-response. 51.9% of surveys land 1-2 days after the contact (stored in the contact's partition). |
| `call_transcripts.interaction_id` -> interactions | 171,321/171,321 resolve; 25.0% of contacts | no semantic content (see 1.1) |
| `customer_id` interactions/complaints/surveys/transactions/sends -> `customers` | 0 orphans in all of them; 148,443 customers have a contact, 54,145 a PQR, 113,640 a survey, 134,515 a transaction, 150,000 a send; 53,593 customers have both contacts and PQRs | usable. Customer attributes (country, segment) show no effect on any outcome. |
| `transactions.product_id` -> `products` | 0 orphans; the product owner always equals the transaction customer; only Active products transact | usable |
| `complaints.affected_product_id` -> `products` | 33.6% null; of the non-null, **100% (44,570) belong to a DIFFERENT customer than the complaint's customer** | NOT usable as a link; `affected_product` type/status carry no signal (SLA 18-23% across types) |
| `complaints.related_branch_id`, `transactions.branch_id` -> `branches` | 71.4% and 68.6% null; every non-null value resolves (0 orphans among non-null) | usable only for the minority with a branch; null is structural (non-branch channels) |
| `customers.registration_branch_id`, `service_agents.assigned_branch_id` -> `branches` | 149,995 / 150,000 and 1,198 / 1,200 orphans | broken |
| `complaints.assigned_agent_id` -> `service_agents` | 0 orphans | usable |
| `campaign_sends.campaign_id` -> campaigns, `customer_id` -> customers | 0 orphans | usable |
| E0 `case.complaint_id` -> `complaints.complaint_id` | **2,000 of 2,000 resolve** (subcategory split 1,001 Cobro indebido / 999 Cargo no reconocido; reception channel consistent with E0 channel; E0 opened-month distribution equals the bank creation-month distribution) | usable: gives each E0 case its bank PQR attributes (bank `sla_breached` = 21.7%, 433/2,000) |
| E0 `case.customer_id` -> `customers` | pseudonymised, fewer than 10 of 2,000 resolve | NOT linkable to bank contacts, surveys or transactions |

### 1.6 Data-quality caveats that change what a sensor may claim

- Contacts: `contact_reason` duplicates `reason_category`; `was_resolved` mixes every complaint type; `Web` = video; duration/wait nulls are structural by `interaction_type`. 175 contacts (and 29 PQRs) have timestamps after the last partition (2026-06-17). Transcripts and sentiment carry no independent semantics.
- PQR: `subcategory` 1:1 with category; `sla_breached`, `status`, `is_repeat_complainer` behave as independent random flags; `resolution_date` leaks the future; 22,525 null and 44,570 wrong-owner product links; 71.4% null branch (the non-null resolve).
- Transactions: 77% null merchant, 61% null category, 57% null amount_usd, 68.6% null branch; 87,860 transactions belong to customers whose status is Closed (2.0% of customers still transact and contact at the same rate as Active ones).
- Marketing: `failure_reason` "SMTP error" and "Invalid email address" appear on SMS, Push, WhatsApp and Voice sends (channel-inconsistent), `subject` contains the literal "nan" (quality report F3b), 0.47% of sends are dated after the campaign end.
- Digital: 600 `app_version` values (about 600 events each per sampled day) make version-level cells useless; `Error` events are not a validated technical-failure taxonomy (spec F2 row "Digital").
- Documented row counts are wrong by -11% to +56% (quality report F4): report real counts only.

## 2. What the dates really support

Measured, not assumed:

1. Naive, second precision, same format everywhere; no zone marker. Hour-of-day is UNIFORM in every table (contacts 28.3k-29.1k per hour; transactions 183.6k-185.2k; PQR 2.7k-2.9k; digital 21.7k-23.5k per sampled hour): there is no intraday or business-hours structure to analyse.
2. Each table has a FIXED offset between its naive timestamp and its partition date (`process_date`), identical in every month and year (no DST jump over 2023-2026): contacts and PQR roll over at 08:00 naive (`date(ts - 8 h) == process_date`), transactions, campaign sends and digital events at 06:00 (`ts - 6 h`, i.e. the documented UTC to UTC-6 case), surveys are stored in the CALL's partition (survey_date up to +2 days later). The data-pipeline claim "timestamps UTC, partition UTC-6" holds for transactions only: contacts/PQR show 8 h, so the naive clocks are NOT proven to be one common clock; a 2 h table-to-table inconsistency cannot be resolved from the data.
3. Therefore: (a) a literal-month cohort inside one table is internally consistent; at most about 1.1% of a month's rows (those within 8 h of a boundary) could belong to the adjacent month under another clock, immaterial because every rate is stationary; use `process_date` month as a sensitivity run (identical for all contact rows). (b) Do NOT order events across tables below day level, convert to UTC, or do hour-of-day / business-hours / SLA-clock arithmetic. (c) Do NOT build "as-of cutoff" views from final-extract outcomes (resolution up to +31 d after creation and 213 PQRs resolved after the extract end, surveys +1-2 d, sends' opens/conversions up to +11 d, all stored in the original event partition).
4. Partial months: 2023-06 (from the 17th) and 2026-06 (to the 18th). Use the 35 full months 2023-07..2026-05 for rates; keep partial months only for volumes marked partial.
5. Stationarity: monthly dispersion and trend tests found NO drift (contact unresolved chi2/df 0.81, Queja unresolved 1.10, Queja share 1.07, escalation 0.96, PQR SLA 0.96, PQR open-like 0.99, CSAT/CES low 0.83, transaction declines 1.01; all trend p > 0.4). Only campaign conversion is overdispersed by month (7.8) and that is channel mix (within Email 1.05, SMS 1.01, Push 0.75).

### 2.1 Replication designs (recommended order)

Because outcomes are final-extract, rows are exchangeable inside a reason, customers are independent (design effect ~ 1: P(unresolved) is 0.2330 after a prior unresolved contact vs 0.2328 after a resolved one; agent dispersion 0.97) and there is no temporal structure, the cleanest valid designs are cross-sectional:

- R1 PRIMARY, customer-hash split. `h = SHA-256(salt || customer_id) mod 2` (salt fixed in the run manifest). Discover on A (enumerate and register ALL cells, test each against "rest of the same channel", Benjamini-Hochberg q = 0.01 or Bonferroni over all explored cells, min effect 5 pp absolute and ratio >= 1.25, min n 500 over the full period, never per 30 d), confirm only the A-selected cells on B (same direction, one-sided, Bonferroni over the number selected). Customers are never split across halves, so no leakage; ICC ~ 0 so plain two-proportion tests are valid. Evidence it works here: Queja effect +39.67 pp in A, +40.01 pp in B.
- R2 SECONDARY, two long windows: discovery 2023-07..2024-12 (18 months), replication 2025-01..2026-05 (17 months), same direction in both windows AND in at least 80% of full months for cells with n >= 100/month. Valid within one table because the offset is constant; label `windows=literal_naive_month`, `outcome=final_extract`. Evidence: Queja +39.96 pp vs +39.72 pp; 37/37 months. This confirms PERSISTENCE of a level; it cannot detect emergence (nothing emerges).
- R3 STRATA robustness (cheap, run always): channel (6), country (3), segment (4), year (4), agent-hash half. A finding must hold in >= 2/3 of strata with the same sign and be pooled by Mantel-Haenszel over channel. Queja: all 6 channels +39.6 .. +41.0 pp.
- R4 NEGATIVE CONTROLS and the spec F2 permutation test: permute the reason labels within channel x month; expect zero admitted cells; also run on the non-differentiating dimensions (channel, country, segment, agent) and expect `refuted/no differential`. Never turn the coarse category `Queja` into a cause.
- Spec 455 temporal profile (discovery [T-60d,T-30d), confirmation [T-30d,T), n_known >= 500 per cell per period): with 35 full months, cell sizes per 30 d for reason x channel are: Phone 191 of 222 cells >= 500 (Retencion/Phone averages 471, Comercial 1,256, Queja 2,687); App, Email, Web Chat, WhatsApp: 0 cells >= 500 (median 98-120; Web median 15). For PQR (about 1,800 per month in total, about 360 per category) NO category cell reaches 500 in 30 d. So the profile degenerates to `insufficient_evidence` outside Phone contacts; use 90-180 d windows or pool the four digital channels, and never shorten after looking.
- Spec 455 bootstrap by customer (2,000 resamples): needs customer-level data. With the aggregator, approximate it with `cust_bucket` (see T2) as the resampling unit (40 buckets of about 3,700 customers).

Limits to state in every finding: descriptive only, final-extract facts, no causality, no savings; effects are the generator's reason mix, not bank prevalence; `corroborated_descriptive` is the ceiling for bank findings.

## 3. Candidate findings

Notation: "unres" = `was_resolved = false`. Contacts population = all 686,296 contacts (35 full months for monthly series). Effects are shares (no cell < 10). CIs are normal-approximation 95%. "Replicates" = under the recommended design (R1 + R2 + R3). F2 families: C = atencion/contactos, P = PQR/SLA, T = transacciones/rechazos, D = friccion digital, M = marketing, X = productos/cartera descriptiva, H = salud del motor / calidad de datos, S = experiencia/operacion (CSAT, agentes), PL = plataforma observada, E0 = E0 profile.

| ID | Candidate | Class | Family | Status expected |
|---|---|---|---|---|
| F01 | Queja contacts are far more often unresolved | problem | C | corroborated_descriptive |
| F02 | Retencion, Comercial and Tecnico contacts are unresolved at 30-40% and have no specialist agent | problem | C | corroborated_descriptive |
| F03 | Handling effort is spent on contacts that stay unresolved | inefficiency | C, S | corroborated_descriptive (derived of F01/F02) |
| F04 | Survey scores collapse for unresolved contacts | descriptive-only (dependent) | S | descriptive |
| F05 | PQR handling speed ignores priority | inefficiency / risk | P | candidate_descriptive |
| F06 | 75% of PQRs are Open/In Process/Escalated, 30% have no assigned agent | descriptive-only (artifact suspect) | P | descriptive, flagged |
| F07 | PQR SLA breach rate differs by category/channel | NON-FINDING (flat) | P | refuted / no differential |
| F08 | Marketing sends ignore consent | risk | M | corroborated_descriptive |
| F09 | Campaigns differ persistently in conversion | descriptive-only | M | candidate_descriptive |
| F10 | Digital Error events concentrate on transactional actions | descriptive-only | D | corroborated_descriptive |
| F11 | Broken referential and structural integrity | risk (data) | H | unsupported-link notices |
| F12 | Transaction declines differ by type/channel/country/month | NON-FINDING (flat) | T | refuted |
| F13 | Recontact, heavy users, agent outliers, wait/escalation | NON-FINDINGS (flat/random) | C, S | refuted |
| F14 | E0: advisors run the same transactions query in 79% of dispute cases | inefficiency | E0 | candidate_descriptive |
| F15 | E0: 25% of over-limit provisional-credit requests are rejected | inefficiency / risk (low power) | E0 | candidate_descriptive, weak |

Details follow. Every effect below was recomputed from raw rows in this audit.

### F01 Unresolved contacts, Queja (M1)
- Metric `contact_unresolved@1`: numerator = contacts with `was_resolved=false`; denominator = contacts with a known flag (100% coverage); grain = contact; population = all contacts in the period; cell = reason x channel; comparator = all other reasons in the same channel.
- Effect: Queja 66,000 / 117,021 = 56.40% vs rest 94,266 / 569,275 = 16.56%; difference +39.84 pp [+39.54, +40.14].
- Recurring: 37/37 months (difference +37.8 .. +42.1 pp, monthly n >= 9,012), all 4 calendar years (+39.4 .. +40.4 pp), monthly dispersion 1.10.
- Replication: customer halves A/B +39.67 / +40.01 pp; agent halves +39.78 / +39.90; windows W1/W2 +39.96 / +39.72; channels App +39.7, Email +41.0, Phone +39.8, Web +40.5 (n = 588 Queja), Web Chat +39.8, WhatsApp +39.6; Inbound vs Outbound call 56.3% vs 56.9%. Replicates under R1, R2 and R3.
- Class: problem (operational non-resolution), no cause. Queja is 17.05% of contacts and 41.2% of all unresolved contacts. The effect is the same on every channel, so no channel-specific thesis exists.
- Caveat: `was_resolved` mixes every complaint type; `contact_reason` has no sub-reason; no link to PQR.

### F02 Unresolved contacts, other reasons (M1, same definition)
- Rates (unres / contacts): Retencion 8,198 / 20,578 = 39.84%; Comercial 19,093 / 54,879 = 34.79%; Tecnico 30,940 / 102,899 = 30.07%; Producto 15,650 / 150,863 = 10.37%; Transaccional 20,385 / 240,056 = 8.49%. Share of all unresolved contacts: Queja 41.2%, Tecnico 19.3%, Transaccional 12.7%, Comercial 11.9%, Producto 9.8%, Retencion 5.1%. Tecnico + Comercial + Retencion + Producto together carry 73,881 unresolved contacts (46.1%) in reasons for which no specialist agent exists on the platform.
- Replication: each rate is stable within +-1 pp across customer halves (Retencion 39.4/40.3, Comercial 35.0/34.6, Tecnico 30.0/30.1), windows (Retencion 40.0/39.6) and agent halves; flat across channels, countries, segments.
- Class: problem; ranking by volume x rate gives the priorities for an "uncovered reason" proposal. Cells of 3,000+ contacts only for Phone.

### F03 Handling effort on unresolved contacts (derived)
- Metric `handle_time_unresolved_share`: numerator = sum of `duration_seconds` of unresolved contacts; denominator = sum of `duration_seconds`; population = contacts with duration (590,062 = Phone, App and Web video; null for Chat and Email by design); grain = contact.
- Effect: 28.87% of handled time (15,212 of about 52,700 hours) is spent on contacts that stay unresolved; by reason Queja 56.6%, Retencion 39.7%, Comercial 34.9%, Tecnico 30.0%, Producto 10.2%, Transaccional 10.2%. Average handle time by reason: Comercial 540 s (2.4x Transaccional's 221 s), Retencion 479, Queja 435, Tecnico 361, Producto 266. Duration does not depend on the resolved flag except in Transaccional (+48 s, 264.8 vs 216.7, n = 17,515 vs 188,950).
- Class: inefficiency (effort without resolution), but a re-expression of F01/F02 x reason-driven duration; report as one dependent family member, do not add its burden to F01 (spec: burdens are not summed).
- Replication: as F02. Caveat: duration is structurally null for chat/email (14.0%); the share is computed over the 86% phone/video population.

### F04 Survey scores vs resolution (M6)
- Metric `survey_low_score_rate` per survey type (CSAT and CES: score <= 2 on a 1-4 scale; NPS excluded because its 2-7 scale and category thresholds are artifacts); numerator = low scores; denominator = surveys of that type; grain = survey joined to its contact (100% linkable; response coverage 31.0%, flat across reasons).
- Effect: CSAT low 84.9% for unresolved vs 14.9% for resolved contacts (CES 85.2% vs 14.7%); mean score 2.00 vs 3.00; across all types score <= 2 is 69.7% (unresolved) vs 10.4% (resolved). By reason (all types pooled, mixed scales): Queja 43.7% low vs Transaccional 15.4%, but WITHIN each resolved state the reason does not matter (unresolved mean 2.28-2.31, resolved 3.89-3.91 in all six reasons): the reason effect is entirely mediated by resolution. Survey score is unaffected by escalation (24.3% vs 23.9%), wait > 180 s (24.3% vs 24.3%), or contact channel (23.5-24.4%).
- Class: descriptive-only, dependent on F01; NOT an independent problem. The sensor must not rank it as a separate burden. Mean score by month 3.48-3.57 with all types pooled (flat).

### F05 PQR handling speed ignores priority (P)
- Metric `pqr_first_response_hours_median` by priority: median hours from `creation_date` to `first_response_date`, among PQRs with a first response (40,853 = 60.9%).
- Effect: Critical 38 h, High 37 h, Medium 38 h, Low 38 h; median resolution days Critical 15, High 16, Medium 16, Low 16; SLA breach Critical 19.2%, High 20.5%, Medium 20.1%, Low 20.1%. A Critical PQR is not handled faster than a Low one; 26.5% of responded PQRs wait more than 48 h (10,830 of 40,853), 20.6% of those breached.
- Recurring: all 37 months and all categories. Replication: customer halves and categories identical by construction (flat); channel (6) flat. The comparison is "Critical vs Low", discovery on half A, replication on half B.
- Class: inefficiency/risk (priority has no operational effect), caveat: priority may be assigned after the fact in the generator; response times could simply be independent random draws. Status `candidate_descriptive`.

### F06 PQR open backlog and unassigned work (P)
- Metric `pqr_open_rate`: numerator = status in (Open, In Process, Escalated); denominator = all PQRs; grain = PQR; cell = category (and creation year). Also `pqr_unassigned_open_rate` = status Open / all.
- Effect: 50,269 / 67,095 = 74.92% (range by category 74.6-75.2%; monthly 73.3-76.5%); Open (no agent, no first response) 20,125 = 30.0%; 33,452 open-like PQRs are older than 365 days (median age 547 d).
- ARTIFACT FLAG: the open share does not decrease with age (74.7%, 74.9%, 75.1% for ages < 1 y, 1-2 y, 2-3 y); a real backlog would. The status is a snapshot independent of time; treat as `descriptive_only` with `artifact_suspect=true`; never present an "aging backlog" as a finding without that flag.
- Replication: flat in every stratum (this is exactly why it is not a differential finding).

### F07 PQR SLA breach, NON-FINDING (M5)
- Metric `pqr_sla@1`: numerator `sla_breached=true` / PQRs (100% known); cells category x reception channel, comparator rest of same category/channel.
- Effect: 13,495 / 67,095 = 20.11%; categories 19.8-20.4%, channels 19.8-22.5% (Regulator 22.45%, n = 717, difference +2.3 pp, CI +-3 pp, not significant), priority 19.2-20.5%, case type 19.9-21.3%, country 19.8-20.4%, repeat-complainer flag 20.11% vs 20.11%, month 18.1-22.4% (dispersion 0.96). The flag is independent of the response and resolution timestamps (section 1.4).
- Class: NON-FINDING: `refuted / no differential`. Also a data-trust finding: the flag is not derived from the timestamps.

### F08 Marketing sends ignore consent (M)
- Metric `send_to_nonconsenting_rate`: numerator = sends to customers with `accepts_marketing=false`; denominator = sends; grain = send; cell = send channel x month.
- Effect: 874,417 / 1,746,801 = 50.06% of sends go to non-consenting customers; by channel Email 50.06%, Push 50.16%, SMS 50.00%, Voice 50.04%, WhatsApp 50.05%; consent has no effect on conversion (0.55% consenting vs 0.57% non) nor on opens (38.6% vs 38.6%).
- Replication: same in every month and channel (the share equals the base rate of 50.0% of non-consenting customers: sends are independent of consent).
- Class: risk (compliance), `descriptive_only` for the engine (no causal claim). 0.47% of sends are dated after the campaign end and campaign segment targeting is random (e.g. 59.9% of sends targeted to Basic land on Basic customers, the base rate). Not linkable to the five platform agents.

### F09 Campaign conversion heterogeneity (M)
- Metric `conversion_rate` per campaign: `had_conversion` / sends; channels Email, SMS and Push (WhatsApp and Voice have no conversions); campaigns with >= 500 sends (135).
- Effect: campaign conversion ranges 0.24% to 1.10% (median 0.73%), overdispersion chi2/df 4.1; the split-half (customer-hash) correlation of campaign conversion is 0.47, so part of the spread persists. Not adjusted for channel mix (SMS 0.94%, Push 0.78%, Email 0.56%).
- Class: descriptive-only; candidate for the marketing family; no incrementality (no control group).

### F10 Digital Error events on transactional actions (D)
- Metric `digital_error_share` by action: numerator = events with `event_type='Error'`; denominator = events with that action; grain = event; all 15,620,994 events streamed (aggregate-only).
- Effect: overall 358,723 / 15,620,994 = 2.30%; by action: view_transactions 6.00%, initiate_transfer 5.97%, initiate_payment 5.95% vs view_help 4.57%, view_home 4.53%, view_accounts 4.51%, view_products 4.51%; login, logout, view_product 0.0% (structural: no Error events with those actions); null action 2.28%. Group difference +1.44 pp (transactional actions 5.97% of 2,705,088 vs other views 4.53% of 3,565,262).
- Recurring and replication: identified customers half A/B 5.93%/6.01% vs 4.56%/4.50%; channels (4) 5.95-5.99% vs 4.50-4.56%; years 2023-2026 5.96-6.00% vs 4.51-4.56%. Flat by channel, platform, month (2.1-2.7% sampled); no app-version signal (about 600 versions, 400-800 events per version per sampled day, errors 0.7%-4.3% = noise).
- No link to contacts: customers with an Error on a sampled day contact within 7 days at 2.66% vs 3.01% without (not higher).
- Class: descriptive-only (the spec forbids calling `Error` a technical failure without a validated taxonomy); `friction candidate`.

### F11 Integrity and link failures (H)
- Metrics: `fk_orphan_rate`, `null_rate`, `contract_violation_count` per column (sensor family "salud del motor / calidad").
- Facts: `origin_interaction_id` 100% null; 100% wrong-owner `affected_product_id`; customer and agent branch links 99.98% orphan (PQR and transaction branch links resolve where present); 87,860 transactions on Closed customers; `contact_reason` duplicate; subcategory 1:1; random flags (SLA, status, repeat); channel-inconsistent `failure_reason`; documented counts off by -16% to +56%.
- Class: risk (data trust). Output is `unsupported/insufficient_evidence` for the affected links, never a hallucinated chain. Persistent in every month by construction.

### F12 Transaction declines, NON-FINDING (T)
- Metric `tx_decline_rate`: numerator `transaction_status='Declined'` / all transactions (status 100% known); cells type x channel x month, plus customer country, segment, product type.
- Effect: 221,234 / 4,425,008 = 5.00%; by type 4.97-5.06%, by channel 4.96-5.12% (Transfer 5.12%, n = 89,159), by country 4.85-5.01% (including foreign), by customer segment 4.99-5.04%, by product type 4.94-5.20% (Seguro 22,706 transactions at 5.20%), months 4.85-5.16% (dispersion 1.01); fraud 0.098% flat. Response codes are uniform. A decline does not raise the chance of a contact in the next 7 days (2.86% vs 2.89% approved; 25% customer sample, 1.09M transactions).
- Class: NON-FINDING, `refuted`. Pending 2.0% and Reversed 1.0% are equally flat.

### F13 Flat / random indicators (group of NON-FINDINGS)
- Recontact: same customer again within 7 d 2.88% (30 d 11.8%), identical after resolved vs unresolved contacts (2.88% vs 2.88%), after followup vs none (2.90% vs 2.87%); same-reason recontact equals share-driven chance (Transaccional 1.02% = 2.88% x 35%).
- Heavy users: contacts per customer Poisson (mean 4.575, variance 4.584, max 15); customer status and segment do not change contact or PQR rates.
- Agent outliers: dispersion chi2/df 0.97 (unresolved), 0.99 (escalation), 0.96 (followup) over 1,090 agents with 5,458 degrees of freedom; `avg_csat` vs observed CSAT per agent r = -0.01.
- Wait, escalation, channel, country, hour, weekday, accent mismatch: flat (escalation 9.8-10.5% everywhere; wait median 119 s everywhere).
- Class: all `refuted / no differential`. They are the negative controls that a sensor must pass.

### F14 E0 recurring copilot query (E0, see section 4)
### F15 E0 provisional-credit approvals (E0, see section 4)

## 4. The E0 side

E0 = 2,000 dispute cases (every row `topic = disputar_cargo`, `contact_reason = Queja`), opened 2025-01-01 .. 2025-06-30 (339/319/358/328/333/323 per month), channels phone 56.5 / email 18.0 / web_chat 15.1 / app_chat 10.5, language es 95% pt 5%, origin customer 95.4 / branch 3.5 / regulator 1.1, priority medium 49.6 / low 30.3 / high 20.2. Tables: case 2,000, turn 24,049, copilot_query 2,201, tool_call 2,577, identity_check 845, approval 286, routing_step 2,000 (all tier `human`), case_close 2,000, signal 3 (not used). Everything is generator-encoded (frequencies are not bank prevalence); the case clocks are uniform over the 24 h like the bank data.

### Computable from E0
- F14 `e0_recurring_copilot_query`: numerator = distinct cases having the dominant `query_signature` (`transactions|customer_id|last_30d|merchant,amount,city,date`); denominator = cases in the window; grain = case. Overall 1,587 / 2,000 = 79.35%; boot (first 200 by opened_at) 154 / 200 = 77.0%; repro (1,800) 1,433 / 1,800 = 79.6%; conditional on a `crear_disputa` call 80.0% (1,318 / 1,648). Two other signatures: `complaints|customer_id|all|...` 314 cases (15.7%), `products|customer_id|cards|...` 300 cases (15.0%). Stable across channel (78.5-81.8%), language (79.0-79.4%), origin (68-84%, small cells), priority (78.5-80.5%), month (77.1-84.6%), customer half (80.3/78.4), analyst half (79.4/79.3). Min support 20 cases is met by far.
  - IMPORTANT interpretation: it is cross-case recurrence of a lookup, NOT a within-case repeat: each case has at most one query per signature (queries per signature = cases per signature), and 1.10 queries per case on average. The reported "93.1% = 1,433/1,539" could not be reproduced: 1,433 matches the repro numerator, but the denominator is 1,800 (79.6%); 1,539 is not any population I could derive (not the repro cases with `crear_disputa`, 1,648). Re-derive that denominator before citing 93%.
  - 34.8% of answers are sent to the chat (`sent_to_chat`), flat by signature (transactions 34.6%, complaints 33.8%, products 37.7%): a weak proxy for advisor uptake, not a draft-acceptance metric.
  - The three signatures read tables that the copiloto already has tools for (leer_movimientos, leer_pqr_cliente, leer_productos): the signal supports a PROMPT/FLOW change on the copilot, not a new tool.
- F15 `e0_overlimit_abono_rejection`: numerator = abono_provisional approvals with decision `rejected`; denominator = abono approvals; grain = approval. 66 / 264 = 25.0% (all `over_role_limit`); another 22 approvals (regulator replies) are always approved. 51.0% of abono requests need approval (264 / 518); median decision latency 4 min. Weak replication: customer halves 20.9% / 29.6%, analyst halves 27.3% / 22.8%, months 12.8-36.4% (n about 45), channels 14.8-26.8%; boot vs repro 5/28 vs 61/236. `candidate_descriptive`, low power.
- Also computable: resolved at contact 94/2,000 = 4.7% (all `explained`), followup present 91.8%, CSAT 1-4 for 30% (mean 2.15; 1,399 null), tool mix (crear_disputa 1,847 calls in 1,835 cases, abono_provisional 452, bloquear_tarjeta 256, responder_regulador 22), tool timeout 12 / 2,577 = 0.47% (all `crear_disputa`; retries 0.006 per call), identity checks 845 all `verified` (0 failures), routing outcome mitigated 1,835 / resolved 94 / abstained 71, analyst concentration (808 analysts, 89 with >= 5 cases, max 40), bank PQR attributes through `complaint_id` (subcategory, bank `sla_breached` 21.7%).

### E0 cannot support
- Draft acceptance / edit ratio / agent-resolved (`turn.from_suggestion_id` is 100% null; no `suggestion` table); stage 3 and "agent proposed" in the maturity model.
- Any case type other than card disputes (single topic), non-dispute reasons, or comparison between topics.
- Any temporal change (six stationary months, generated), onset detection, drift, or an as-of view (all outcomes are in `case_close`; `labels` are evaluator-only).
- Analyst-level performance (about 2.5 cases per analyst; cells < 10).
- Queue wait, handle time or SLA (case close median 0 h, mean 4.5 h; `sla_due_at` is constant 360 h; closed-after-SLA 0%).
- Technical-error detection beyond 12 timeouts; identity failures (none).
- Joins to bank contacts, surveys or transactions (`customer_id` pseudonymised); the `complaint_id` join is the only bank link.
- Prevalence, causality or savings for the bank (spec: facts valid inside the E0 environment).

## 5. Mapping findings to platform agents and improvement kinds

Platform agents (platform attach plan section 1.5 and the artifact anatomy doc): `recepcion` (customer chat entry, routes only to `disputas` and `consultas`; template + classifier driven), `disputas` (card-charge dispute; prompt `p/resumen_radicado`), `consultas` (PQR status; static template `t/estado_pqr`), `copiloto-asesor` (advisor copilot; prompt `p/copiloto`, read tools `leer_movimientos`, `leer_productos`, `leer_pqr_cliente`, `obtener_handoff`, `leer_transcript`), `constructor-chat` (builder only). Treatable population caveat: 85% of bank contacts are Phone; customer-facing agents are chat agents (chat/email/video = 15% of contacts); only the copilot can touch phone work.

| Finding | Agent | Improvement kind | Link grade | Reason / limits |
|---|---|---|---|---|
| F01 Queja unresolved | `disputas` (for card disputes) ; new agent for non-dispute complaint types ; `recepcion` routing card | prompt (`p/resumen_radicado`), template, new `agent` + routing card | mechanism_proxy at best | Contacts have no sub-reason, PQR and contact are unlinkable. Only 36.5% of PQR (Fees + Transactions categories) are dispute topics; 53.5% (Technical, Branch, Service) have no specialist. Effect on contact resolution is not evaluable natively (no oracle on `was_resolved`). |
| F02 Tecnico / Comercial / Retencion / Producto unresolved | new agent (e.g. `soporte-app` closure-copied from `consultas`) + `recepcion` routing/classifier; `copiloto-asesor` for phone | `agent` (priority 1), routing card, template | mechanism_proxy | `recepcion` has no specialist for these reasons (46.1% of unresolved contacts). WHERE is known, WHY is not. Proposal must be a narrow intake/escalation agent, not a claim of resolution gain. |
| F03 Handle time on unresolved | `copiloto-asesor` | prompt (`p/copiloto`), flow (`asistir`) | unlinked to `not_evaluable` | Core eval has no timing metric for advisor work; derived of F01/F02. |
| F04 CSAT | none | none | `unlinked` | Dependent metric; no action target of its own. |
| F05 PQR ignores priority | none | policy (non-protected) / flow | `unlinked` | PQR back-office handling is not an agent on the platform; closest, `consultas`, only reads status. |
| F06 Open backlog | `consultas` (status template only) | template (`t/estado_pqr` with real status) | `unlinked` for the backlog itself | Artifact suspect; improving the status message does not reduce the backlog. |
| F07 SLA flat | none | none | non-finding | Report no differential. |
| F08 Consent | none | policy (marketing consent gate) | `unlinked` | No marketing agent; outside platform scope. |
| F09 Campaign heterogeneity | none | none | `unlinked` | No agent; no incrementality. |
| F10 Digital Error actions | new `soporte-app` (Tecnico) at most | `agent` | `unlinked` (no error -> contact link) | No evidence that errors drive contacts (2.66% vs 3.01%). |
| F11 Integrity | engine health | `unsupported` notices | n/a | Data contract, not a platform change. |
| F12, F13 | none | none | non-findings | Negative controls. |
| F14 repeated copilot query | `copiloto-asesor` | prompt (`p/copiloto`: gather charges, PQR history and products in one answer for disputes), flow `asistir`, existing tool link (the three read tools already in `tools_allowed`) | mechanism_proxy | New tools are paused; the lookups already exist. Evaluate with scripted copilot scenarios; no draft acceptance data. |
| F15 abono rejections | `disputas` / `copiloto-asesor` | prompt (limit-aware guidance); policy is protected | `unlinked` for policy change | R4 amount policy is protected; low power. |

Honest staging for the demo: bank findings F01/F02 define WHERE (population, priority, ranking) and justify an "uncovered reason" new-agent or routing proposal; F14 gives the concrete, mechanism-level proposal; neither gives causal savings.

## 6. Minimal aggregator spec (Python, DuckDB or pyarrow) for a Rust cells sensor

Principle: the aggregator emits TREATED CELL TABLES (NDJSON or Parquet), one file per table with a manifest; the Rust sensor never sees rows. No identifiers, no free text, no timestamps finer than the month, normalized closed vocabularies (section 1.3), integers only.

### 6.1 Common rules
- Period: literal `YYYY-MM` from the naive event timestamp (`interaction_date`, `creation_date`, `survey_date`... ; surveys keyed by the CONTACT month); exclude the two partial months from rate cells or flag `partial=true`; manifest records `timestamp_semantics=naive_literal_month`, `outcomes=final_extract`.
- Replication key: `split` in {`A`,`B`} = SHA-256(salt || customer_id) low bit; `salt` committed in the manifest. (Surveys and PQR inherit the customer; digital anonymous events get `split=U` and are used only in overall tables.) Optional `cust_bucket` in 0..39 for cluster resampling (T2 only).
- k rule: a cell row is emitted only if `n_rows >= 10`; every binary measure is published as `(valid, pos)` and BOTH are replaced by null with flag `suppressed=true` if `pos` or `valid - pos` is in 1..9 (a zero is published only when `valid >= 10`; the sensor treats null as missing, never as 0); no margin totals are published; rows below k are dropped and not folded into `_other` unless the combined residual is itself >= 10 (a single suppressed cell is never recoverable by differencing); the manifest carries only `suppressed_any=true/false` per table, never exact suppressed counts (consistent with the Codex projection doc).
- Measures for mean/variance: `n`, `sum`, `sumsq` (so the sensor can compute means and CIs); medians are not emitted.
- Provenance: `source_table`, `source_file_digest_set`, `aggregator_version`, `k=10`, `policy_version=2`.

### 6.2 Tables

| Table | Grain (columns) | Measures | Rows after k=10 (computed) |
|---|---|---|---|
| T1 `contact_cells` | period x reason(6) x channel(6) x country(3) x split(2) | `n_contacts`; `(valid,pos)` for unresolved, followup, escalated, negative_sentiment; `n/sum/sumsq` of duration_seconds and wait_time_seconds; `n_survey`, `n_csat_ces`, `n_csat_ces_low` (score <= 2), `n_nps` | 4,969 rows (of 7,650 possible; keeps 98.3% of contacts); without split 3,018 rows (99.4%) |
| T2 `contact_bucket_cells` | reason(6) x channel_group(`phone`,`digital`) x cust_bucket(40) x half_year(6) | `n_contacts`, `n_unres` | 3,071 rows (99.8% of contacts) |
| T3 `contact_recontact` (negative control) | period x first_reason(6) | `n_eligible`, `n_recontact_7d`, `n_recontact_30d`, `n_recontact_same_reason_7d`, `n_recontact_same_reason_30d` | 222 rows |
| T4 `pqr_cells` | period x category(5) x reception_channel(6) x split(2) | `n_pqr`; `(valid,pos)` for sla_breached, status_open, status_in_process, status_escalated, status_closed_like (Resolved+Closed+Rejected), has_first_response, has_assigned_agent, has_resolution, subcategory_missing, repeat_flag, compensation; `n/sum/sumsq` first_response_hours and resolution_days; `n_fr_gt_48h`; `n_open_gt_365d` | 1,534 rows (96% of PQRs). Companion `pqr_priority_cells` period x category x priority x split: 1,260 rows (97.7%); coarser `pqr_month_category` (period x category x split) 370 rows (100%) as the fallback for n >= 500 questions |
| T5 `survey_cells` | quarter x reason(6) x was_resolved(2) x survey_type(3) x split(2) | `n_surveys`, `n_low`, `sum_score`, `sumsq_score` | 896 rows (99.9%) |
| T6 `tx_cells` | period x type(6) x channel(6) x status(4) x response_code(5 incl. none) x split(2) | `n_tx`, `n_fraud`, `n_amount_known`, `sum_amount_usd` | 16,365 rows (98.3%); 11,469 without split |
| T7 `digital_cells` | period x channel(4) x event_type(7) x action(12 incl. none) x split(3: A,B,U) | `n_events`, `n_identified` | about 148 distinct (channel, event_type, action) combinations x 36 months x split about 5,300 to 16,000 rows (estimate from the day-15 sample; compute exactly at build) |
| T8 `marketing_cells` | period x send_channel(5) x accepts_marketing(2) x send_status(4) | `n_sends`, `n_delivered`, `n_opened_known`, `n_opened`, `n_clicked`, `n_conversion`, `n_after_campaign_end`, `sum_send_cost` | 1,209 rows (100%) |
| T8b `campaign_cells` | campaign_bucket (campaign id replaced by a stable hash token) x send_channel x split | `n_sends`, `n_conversion` | about 135 campaigns x 3 channels x 2 splits, about 800 rows |
| T9 `product_snapshot` | product_type(8) x product_status(4) x dpd_bucket(6) x country(3), no period (`snapshot=true`) | `n_products` | 220 rows (99.9%) |
| E1 `e0_case_marginals` | long format: dim(`channel`,`language`,`origin`,`priority`,`month`,`bank_subcategory`,`split_boot_repro`,`half`) x value | `n_cases`, `n_dominant_query`, `n_cp_query`, `n_pr_query`, `n_resolved`, `n_followup`, `n_csat_known`, `n_csat_low`, `n_crear_disputa`, `n_abono`, `n_abono_needing_approval`, `n_abono_rejected`, `n_tool_timeout`, `n_sent_to_chat` | about 40 rows; k = 10 applied to cases, so origin `regulator` (22) survives, pt x origin cells do not |
| E2 `e0_signature_cells` | query_signature(3) x split_boot_repro(2) | `n_cases_with_signature`, `n_queries`, `n_cases` | 6 rows |

Estimated total: about 30,000 to 40,000 rows, roughly 8-12 MB as NDJSON (about 3 MB Parquet); aggregation runtime minutes (the 15.6M-row digital stream takes about 30-60 s in DuckDB).

### 6.3 What the sensor does with these cells (so the tables are sufficient)
- Discovery: enumerate every `(table, metric, reason/category, channel)` cell on split A, rank by weighted difference vs "rest of the same channel", BH over all explored cells, min n 500 over the full period and min effect 5 pp.
- Replication: confirm selected cells on split B; recurrence over periods (>= 80% of full months same sign) and strata (channel/country), via T1/T4 period and dimension columns; cluster-aware interval from T2 buckets.
- Negative controls: T3, and permuting `reason`/`category` labels within `period x channel` (spec F2).
- Flat-cell reporting: when no cell passes, emit `refuted/no differential` for F07, F12, F13 (they are the proofs that the sensor does not fabricate findings).
- Artifact guards (configurable): `status_independent_of_age` test on T4 (`n_open_gt_365d` vs `n_open` by age strata), derived-metric rule (followup superset of unresolved; CSAT given resolved), and the wrong-owner/null-link notices of F11.

## 7. Risks and recommendations for the simplest valuable sensor

1. Build only T1, T4, T5, E1/E2 first (about 7,800 rows): they carry F01-F07 and F14/F15, i.e. every finding that can feed a proposal; add T3 as the negative control. T6-T9 only to prove "no signal" on the other spec families (F12) and to show that the engine can also say no.
2. Never present F04, F06, F13 or the flat metrics as problems; they exist to show restraint. The honest headline of the bank data is: one strong reason effect, many flat indicators.
3. Treat the star story numbers carefully: "PQR open 74.9%" is an artifact (flag it); "top 10% of customers hold 41.7% of PQR" and "repeat flag 15%" are Poisson/random effects; "93.1% holdout" needs a denominator check; the SLA flag is not a derived SLA.
4. Do not force a temporal split anywhere except Phone contacts and whole-table PQR; do not claim emergence; use R1 as the default and say so in `result.json`.
5. If a stronger demo is needed the data cannot supply it: the real source of temporal structure or contact -> complaint chains would have to be platform events, not this CSV.

## 8. Open questions

- Which clock is right for contacts/PQR (8 h) vs transactions/digital (6 h)? Ask the dataset owners; the engine can proceed with literal months.
- Is the `requires_followup` superset rule intended (all unresolved require follow-up)? If so it should be a derived column in the contract.
- Whether `status`, `sla_breached` and `is_repeat_complainer` are meant to carry information; if not, mark them `non_informative` in the `SourceContract` so sensors skip them by contract rather than by test.

## 9. Hygiene log

- Row-level material: one DuckDB file (`work.duckdb`) and helper scripts in the session scratchpad, selected non-PII columns only (no names, no free text, no transcripts, no survey comments, no complaint descriptions); the DuckDB file was deleted at the end. No raw row, identifier or cell < 10 appears in this report.
- One process lapse, disclosed: an early profile query printed the distinct values and suppressed counts of one timestamp-typed column (`complaints.closing_date`) to my local tool output before I fixed the suppression helper, and the E0 `turn.text_source` batch labels (not text) were printed with counts. Neither appears in this report, nothing was written to disk, and no identifiers were involved.
- Not done: no edits to any repo, nothing committed, nothing under `D:\Nexus`, no network or model calls. `transactions` and `digital_events` were processed as streamed aggregates only (`digital_events` profile from a day-15 sample plus full-stream grouped error shares).
