# HEDIS Measures - Comprehensive Overview

## Table of Contents
1. [What is HEDIS?](#what-is-hedis)
2. [Measure Categories](#measure-categories)
3. [Key Measures in Detail](#key-measures-in-detail)
4. [Compliance Requirements](#compliance-requirements)
5. [NCQA Audit Process](#ncqa-audit-process)
6. [Data Collection Methods](#data-collection-methods)

---

## What is HEDIS?

### Definition

**HEDIS** = Healthcare Effectiveness Data and Information Set

- Developed and maintained by **NCQA** (National Committee for Quality Assurance)
- Industry-standard set of **~90 performance measures**
- Used by **90% of U.S. health plans**
- Enables **apples-to-apples comparison** across plans

### Purpose

1. **Consumer transparency** - Help people compare plan quality
2. **Performance accountability** - Hold plans responsible for outcomes
3. **Quality improvement** - Drive better care delivery
4. **Financial incentives** - Basis for CMS Star Ratings bonuses

### History

- **1989:** NCQA founded
- **1991:** HEDIS launched (initial 25 measures)
- **1999:** CMS adopts for Medicare reporting
- **2000s:** Expands to ~70 measures
- **2010:** ACA mandates quality reporting
- **2020s:** 90+ measures, adding health equity

---

## Measure Categories

HEDIS measures span **8 domains** of care:

### 1. Effectiveness of Care (40+ measures)
- Preventive care (cancer screenings, immunizations)
- Chronic condition management (diabetes, asthma, hypertension)
- Behavioral health (depression screening, follow-up)
- Respiratory conditions

### 2. Access/Availability of Care (6 measures)
- Adults' access to preventive/ambulatory services
- Children and adolescents' access to PCPs
- Initiation and engagement of treatment

### 3. Experience of Care (7 measures - CAHPS)
- Getting needed care
- Getting care quickly
- Customer service
- Rating of health plan

### 4. Utilization (8 measures)
- Inpatient utilization
- Emergency department visits
- Antibiotic utilization
- Frequency of ongoing prenatal care

### 5. Risk-Adjusted Utilization (6 measures)
- Plan all-cause readmissions
- Emergency department utilization
- Acute hospital utilization

### 6. Health Plan Descriptive Information (4 measures)
- Enrollment by product line
- Weeks of pregnancy at enrollment
- Race/ethnicity diversity
- Language diversity

### 7. Measures Reported Using Electronic Clinical Data Systems (8 measures)
- Lab test follow-up
- Medication monitoring
- Cancer screenings

### 8. Medication Management (4 measures)
- Adherence to statins
- Adherence to diabetes medications
- Adherence to hypertension medications
- Medication reconciliation

---

## Key Measures in Detail

### CDC - Comprehensive Diabetes Care

**Full Name:** Comprehensive Diabetes Care  
**Eligible Population:** Adults 18-75 with diabetes (Type 1 or Type 2)  
**Measurement Year:** Calendar year (January 1 - December 31)

**Sub-measures:**
1. **HbA1c Testing** - Blood sugar control test at least once per year
2. **HbA1c Control (<8%)** - Good diabetes control
3. **HbA1c Control (<9%)** - Poor control
4. **Eye Exam** - Retinal/dilated eye exam to screen for diabetic retinopathy
5. **Kidney Monitoring (Medical Attention for Nephropathy)** - uACR or ACE/ARB prescription
6. **BP Control (<140/90)** - Blood pressure management

**Why It Matters:**
- Diabetes affects 34M Americans (~11% of population)
- Leading cause of blindness, kidney failure, amputation
- Proper management prevents $100K+ in complications
- Major driver of Star Ratings (high weight)

**Compliance Targets:**
| Performance Level | HbA1c Testing | Eye Exam | BP Control |
|------------------|---------------|----------|------------|
| 5 Stars | 95%+ | 93%+ | 92%+ |
| 4 Stars | 88-94% | 85-92% | 85-91% |
| 3 Stars | 80-87% | 77-84% | 75-84% |

**Coding Requirements:**
```
Diabetes diagnosis: ICD-10 E10.*, E11.*
HbA1c test: CPT 83036, 83037, LOINC 4548-4, 17856-6
Eye exam: CPT 67028, 67030, 67031, 92002, 92004, 92012, 92014, 92227, 92228
Nephropathy: uACR (LOINC 13705-9, 14958-3), ACE/ARB drugs, nephropathy diagnosis
```

### BCS - Breast Cancer Screening

**Full Name:** Breast Cancer Screening  
**Eligible Population:** Women ages 50-74  
**Measurement Year:** October 1 (2 years prior) - December 31 (current year)  
**Look-back:** 27 months

**Numerator:** Mammogram (bilateral or unilateral) during measurement period

**Why It Matters:**
- Breast cancer is #2 cancer killer of women
- Early detection (Stage 0-1): 99% 5-year survival rate
- Late detection (Stage 4): 27% 5-year survival rate
- Mammogram costs $100-250 vs $100K+ for late-stage treatment
- 1 in 8 women will develop breast cancer in lifetime

**Compliance Targets:**
| Performance Level | Compliance Rate |
|------------------|----------------|
| 5 Stars | 93%+ |
| 4 Stars | 86-92% |
| 3 Stars | 78-85% |

**Coding Requirements:**
```
Mammogram: CPT 77065, 77066, 77067
             HCPCS G0202, G0204, G0206
             LOINC 24604-1, 24605-8, 24606-6
Bilateral mastectomy (exclusion): ICD-10 Z90.13, CPT 19180, 19182, 19200, 19220, 19240, 19303, 19304, 19305, 19306, 19307
```

**Common Gaps:**
- Member doesn't think it's necessary (no symptoms)
- Fear of mammogram pain
- No transportation to imaging center
- Cost concerns ($40-50 co-pay)
- Scheduling inconvenience (weekday-only availability)

### CBP - Controlling High Blood Pressure

**Full Name:** Controlling High Blood Pressure  
**Eligible Population:** Adults 18-85 with hypertension diagnosis  
**Measurement Year:** Calendar year

**Numerator:** Most recent BP reading <140/90 mmHg

**Why It Matters:**
- Hypertension affects 116M Americans (~46%)
- "Silent killer" - no symptoms until stroke/heart attack
- Uncontrolled BP → stroke ($50K), heart attack ($100K), kidney failure ($90K/year)
- $25/month medication prevents $150K events

**Compliance Targets:**
| Performance Level | BP <140/90 |
|------------------|------------|
| 5 Stars | 92%+ |
| 4 Stars | 85-91% |
| 3 Stars | 75-84% |

**Coding Requirements:**
```
Hypertension: ICD-10 I10-I15
BP reading: LOINC 8480-6 (systolic), 8462-4 (diastolic)
Outpatient visit: CPT 99201-99205, 99211-99215
Telehealth: CPT 99441-99443, G0438-G0439, G2012, G2010
ESRD exclusion: ICD-10 N18.6, Z99.2
Pregnancy exclusion: ICD-10 O10-O16, Z34, Z36
```

**Common Gaps:**
- No recent PCP visit (no BP recorded)
- Home BP monitor not synced to EHR
- Telehealth BP reading not documented correctly
- Member non-adherent to medications

### COL - Colorectal Cancer Screening

**Full Name:** Colorectal Cancer Screening  
**Eligible Population:** Adults 50-75  
**Measurement Year:** Multi-year look-back
- Colonoscopy: 10 years
- Flexible sigmoidoscopy: 5 years
- FIT DNA test: 3 years
- FIT test: 1 year

**Why It Matters:**
- Colorectal cancer is #3 cancer killer
- 95% survival rate if caught early
- Screening reduces incidence by 40% (removes pre-cancerous polyps)
- Treatment costs: $100K-300K vs $600 colonoscopy

**Compliance Targets:**
| Performance Level | Compliance Rate |
|------------------|----------------|
| 5 Stars | 90%+ |
| 4 Stars | 83-89% |
| 3 Stars | 72-82% |

**Coding Requirements:**
```
Colonoscopy: CPT 44388-44408, 45355, 45378-45398, G0105, G0121
Flexible sigmoidoscopy: CPT 45330-45347, G0104
FIT test: CPT 82270, 82274, HCPCS G0328, LOINC 14563-1, 14564-9, 14565-6, 27396-1, 27401-9, 27925-7, 27926-5, 29771-3, 56490-6, 56491-4, 57905-2
FIT-DNA: CPT 81528
```

**Common Gaps:**
- Fear of colonoscopy (invasive, sedation, bowel prep)
- Scheduling inconvenience (day off work, driver needed)
- Cost ($150-500 co-pay)
- Lack of awareness (no symptoms)
- Embarrassment discussing colon health

### CIS - Childhood Immunization Status

**Full Name:** Childhood Immunization Status  
**Eligible Population:** Children who turn 2 during measurement year  
**Measurement Year:** By 2nd birthday

**Vaccines Required (Combo 10):**
1. DTaP (4 doses)
2. IPV (3 doses)
3. MMR (1 dose)
4. HiB (3 doses)
5. Hepatitis B (3 doses)
6. VZV (1 dose)
7. Pneumococcal conjugate (4 doses)
8. Hepatitis A (1 dose)
9. Rotavirus (2-3 doses depending on vaccine type)
10. Influenza (2 doses)

**Why It Matters:**
- Prevents deadly childhood diseases
- Herd immunity protection
- Required for school entry
- Vaccine-preventable disease outbreaks

**Compliance Targets:**
| Performance Level | Combo 10 Rate |
|------------------|---------------|
| 5 Stars | 85%+ |
| 4 Stars | 75-84% |
| 3 Stars | 65-74% |

### Medication Adherence Measures (Part D)

**Three Key Measures:**

1. **Statins** (Adherence to Statins - AST)
   - For cardiovascular disease
   - PDC (Proportion of Days Covered) ≥80%

2. **Diabetes Medications** (Adherence to Diabetes Medications - ADD)
   - Oral hypoglycemics
   - PDC ≥80%

3. **RASA Medications** (Adherence to RASA - ARA)
   - ACE inhibitors or ARBs for hypertension
   - PDC ≥80%

**PDC Calculation:**
```
PDC = Days Covered / Days in Measurement Period

Example:
- Measurement period: 365 days
- Member has medication for 300 days
- PDC = 300/365 = 82.2% ✅ (meets ≥80% threshold)
```

**Why It Matters:**
- Non-adherence causes 125,000 deaths/year
- Costs $100-300B in preventable medical costs
- 50% of chronic disease medications are taken incorrectly
- Medication adherence directly prevents ER visits/hospitalizations

**Compliance Targets:**
| Performance Level | PDC ≥80% Rate |
|------------------|---------------|
| 5 Stars | 88%+ |
| 4 Stars | 82-87% |
| 3 Stars | 75-81% |

---

## Compliance Requirements

### NCQA Audits

**Process:**
1. **Annual data submission** - Health plans submit HEDIS data to NCQA by June 30
2. **NCQA validation** - Random sample of records audited
3. **Certification** - Plans receive "NCQA Certified" or "Reportable" status
4. **Publication** - Results published in Quality Compass (industry benchmark database)

**Audit Types:**

**Level 1: HEDIS Compliance Audit**
- Random sample of 411 medical records per measure
- Verify numerator/denominator compliance
- Check coding accuracy
- Review data collection procedures

**Level 2: IDSS (Information Data Set System) Audit**
- Validate IT systems and processes
- Review data extraction logic
- Test data integrity

### Documentation Requirements

**HEDIS Rule:** "If it's not documented, it didn't happen"

**Valid Documentation:**
- **Medical record** - Progress notes, lab results, imaging reports
- **Claims** - Properly coded procedures
- **Pharmacy** - Fill records with NDC codes
- **Supplemental data** - Lab feeds, HIE data (if validated)

**Invalid Documentation:**
- Member self-report ("patient states she had mammogram")
- Verbal orders without documentation
- Appointment scheduled but not completed
- Results pending

### Hybrid vs Administrative Measurement

**Administrative (Claims-Only):**
- Use claims/encounter data only
- Easier to collect
- Lower compliance rates (misses care not properly coded)
- Used by smaller plans

**Hybrid (Claims + Medical Records):**
- Use claims PLUS manual chart review
- Higher compliance rates (captures undocumented care)
- Labor-intensive (medical record abstraction)
- Preferred by larger plans

**Example Impact:**
```
Measure: Diabetes HbA1c Testing

Administrative only:
- Claims show: 7,200 of 10,000 diabetics had HbA1c test
- Rate: 72%
- Star Rating: 2.5 stars

Hybrid (claims + chart review):
- Claims: 7,200 tests
- Chart review: Find 1,300 additional tests done but not coded
- Total: 8,500 of 10,000
- Rate: 85%
- Star Rating: 4.0 stars

Difference: +1.5 stars from better data collection!
```

---

## NCQA Audit Process

### Timeline

| Month | Activity |
|-------|----------|
| **Jan-Feb** | Final data collection for prior year |
| **March** | Submit draft HEDIS data to NCQA (dry run) |
| **April-May** | NCQA preliminary review, plan corrections |
| **June 30** | Final HEDIS submission deadline |
| **July-Aug** | NCQA audit (if selected) |
| **Sept** | NCQA issues final rates |
| **October** | CMS publishes Star Ratings using HEDIS data |

### Common Audit Findings (Result in Rate Reductions)

1. **Overcounting numerator**
   - Procedure dated outside measurement year
   - Incorrect CPT code
   - Unilateral mammogram counted as bilateral

2. **Undercounting denominator**
   - Missing eligible members
   - Incorrect exclusions

3. **Insufficient documentation**
   - Can't locate medical record
   - Record missing required elements
   - Illegible documentation

4. **Systematic issues**
   - Incorrect measure specification interpretation
   - Coding logic errors
   - Data extraction bugs

**Bias Rate:** Percentage of records with errors

```
Acceptable bias: <5%
Warning: 5-10%
Fail audit: >10%

If fail: HEDIS data marked "Not Reportable"
Impact: Can't use for Star Ratings = lose bonus
```

---

## Data Collection Methods

### 1. Claims/Encounter Data

**Advantages:**
- Automated
- Already collected for payment
- Low incremental cost

**Disadvantages:**
- Depends on accurate coding
- Lags (claims process 60-90 days after service)
- Missing out-of-network care

**Best For:**
- Procedures (mammograms, colonoscopy)
- Lab tests (HbA1c)
- Pharmacy fills

### 2. Medical Record Review (Hybrid)

**Process:**
1. Identify sample of members with gaps (from claims)
2. Request medical records from providers
3. Trained abstractors review records
4. Find "hidden" numerator hits (care provided but not claimed)

**Advantages:**
- Captures undocoded care
- Higher compliance rates (+10-15%)
- More accurate

**Disadvantages:**
- Expensive ($25-50 per record)
- Time-consuming (60-120 days)
- Provider cooperation required

**Best For:**
- Blood pressure readings
- Clinical outcomes (BP control)
- Diagnosis confirmation

### 3. Health Information Exchange (HIE)

**Process:**
- Real-time data feeds from hospitals, labs, pharmacies
- Automated ingestion into data warehouse
- Matches to eligible members

**Advantages:**
- Real-time (no claims lag)
- Captures out-of-network care
- More complete data

**Disadvantages:**
- Requires contracts with HIE vendors
- Data quality varies
- Must pass IDSS audit validation

**Best For:**
- Lab results (HbA1c, eGFR)
- Medication fills (pharmacy HIE)
- Hospital utilization

### 4. Member Portals / Apps

**Process:**
- Member uploads documents (lab results, screening records)
- Plan validates and codes into system

**Advantages:**
- Engages members
- Captures care from any provider
- Low cost

**Disadvantages:**
- Low adoption (<5% of members)
- Requires validation
- NCQA restrictions on self-report

**Best For:**
- Out-of-network care documentation
- Member engagement touchpoints

---

## Resources

- [NCQA HEDIS Measures](https://www.ncqa.org/hedis/measures/)
- [HEDIS Technical Specifications](https://www.ncqa.org/hedis/the-future-of-hedis/)
- [Quality Compass Benchmarks](https://www.ncqa.org/programs/data-and-information-services/quality-compass/)

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-30

