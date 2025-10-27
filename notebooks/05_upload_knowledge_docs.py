# Databricks notebook source
# MAGIC %md
# MAGIC # 05 - Upload Knowledge Documents for MCP
# MAGIC
# MAGIC **Purpose:** Upload HEDIS knowledge documents to Unity Catalog volume
# MAGIC
# MAGIC **Creates:**
# MAGIC - Volume: `humana_quality.hedis_gold.knowledge_docs`
# MAGIC - Documents: HEDIS specifications, NCQA guidelines, quality improvement protocols

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

import sys
import os

# Get current user dynamically
username = spark.conf.get("spark.databricks.workspaceUrl").split("@")[0] if "@" in spark.conf.get("spark.databricks.workspaceUrl") else "vik.malhotra@databricks.com"
bundle_name = "hedis_quality_dashboard"
target = "dev"

# Construct dynamic path
src_path = f"/Workspace/Users/{username}/.bundle/{bundle_name}/{target}/files/src"
sys.path.append(src_path)

print(f"✅ Added to path: {src_path}")

# COMMAND ----------

from utils.table_helpers import create_volume_if_not_exists

# Configuration
CATALOG = "humana_quality"
SCHEMA = "hedis_gold"
VOLUME = "knowledge_docs"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Volume

# COMMAND ----------

create_volume_if_not_exists(spark, CATALOG, SCHEMA, VOLUME)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Knowledge Document 1: HEDIS Measures Guide

# COMMAND ----------

hedis_measures_guide = """# HEDIS Quality Measures Reference Guide

## Overview
Healthcare Effectiveness Data and Information Set (HEDIS) is a comprehensive set of standardized performance measures designed to provide purchasers and consumers with the information they need to reliably compare the performance of health care plans.

## Key HEDIS Measures

### BCS - Breast Cancer Screening
**Description:** Percentage of women aged 50-74 who had a mammogram to screen for breast cancer.

**Eligibility:** Women aged 50-74
**Compliance Criteria:** Mammogram within the past 24 months
**NCQA Target:** ≥ 70%
**Current Performance:** 92%

**Why It Matters:**
- Early detection saves lives
- Significantly improves treatment outcomes
- Reduces mortality by 25-30%

### CDC - Comprehensive Diabetes Care
**Description:** Percentage of members 18-75 with diabetes (type 1 and type 2) who received key preventive services.

**Eligibility:** Members 18-75 with diabetes diagnosis
**Compliance Criteria:**
- HbA1c testing (annual)
- Eye exam (retinal) performed
- Medical attention for nephropathy
- BP control (<140/90)

**NCQA Target:** ≥ 65%
**Current Performance:** 89%

**Why It Matters:**
- Prevents complications (blindness, kidney failure, amputation)
- Reduces hospitalizations
- Improves member quality of life

### CBP - Controlling High Blood Pressure
**Description:** Percentage of members 18-85 with hypertension whose BP was adequately controlled.

**Eligibility:** Members 18-85 with hypertension diagnosis
**Compliance Criteria:** BP < 140/90 mmHg
**NCQA Target:** ≥ 60%
**Current Performance:** 88%

**Why It Matters:**
- #1 controllable risk factor for heart attack and stroke
- Reduces cardiovascular events by 25%
- Cost-effective intervention

### COL - Colorectal Cancer Screening
**Description:** Percentage of members 50-75 who had appropriate screening for colorectal cancer.

**Eligibility:** Members aged 50-75
**Compliance Criteria:**
- Fecal occult blood test (annual), OR
- Flexible sigmoidoscopy (every 5 years), OR
- Colonoscopy (every 10 years)

**NCQA Target:** ≥ 65%
**Current Performance:** 85%

### CIS - Childhood Immunization Status
**Description:** Percentage of children 2 years of age who had four DTP/DTaP, three polio, one MMR, three H influenza type B, three hepatitis B, one chicken pox vaccine, and four pneumococcal conjugate vaccines by their second birthday.

**Eligibility:** Children age 2
**NCQA Target:** ≥ 75%
**Current Performance:** 90%

### W15 - Well-Child Visits (First 15 Months)
**Description:** Percentage of children who had six or more well-child visits with a PCP during their first 15 months of life.

**Eligibility:** Children in first 15 months
**NCQA Target:** ≥ 65%
**Current Performance:** 88%

### AWC - Adolescent Well-Care Visits
**Description:** Percentage of adolescents 12-21 who had at least one comprehensive well-care visit with a PCP or OB/GYN during the measurement year.

**Eligibility:** Adolescents 12-21
**NCQA Target:** ≥ 55%
**Current Performance:** 79%

### PPC - Prenatal and Postpartum Care
**Description:** Percentage of deliveries that received prenatal and postpartum care.

**Eligibility:** Women who delivered a live birth
**Compliance Criteria:**
- Prenatal visit in first trimester or within 42 days of enrollment
- Postpartum visit 7-84 days after delivery

**NCQA Target:** ≥ 75%
**Current Performance:** 87%

## Stars Ratings

HEDIS measures are a key component of Medicare Stars ratings:

- **5 Stars:** Top performance (90th percentile+)
- **4 Stars:** Above average (75th-89th percentile)
- **3 Stars:** Average (50th-74th percentile)
- **2 Stars:** Below average (25th-49th percentile)
- **1 Star:** Low performance (<25th percentile)

**Current Overall Rating:** 4.5 Stars (92nd percentile)

## Gap Closure Best Practices

1. **Prioritize High-Impact Measures**
   - Focus on measures with largest scoring impact
   - Target BCS, CDC, CBP first

2. **Risk Stratification**
   - High-risk members get intensive outreach
   - Medium-risk get standard outreach
   - Low-risk get automated reminders

3. **Multi-Channel Outreach**
   - Phone calls (highest success rate)
   - Text messages (good for younger members)
   - Portal messages
   - Postal mail (for hard-to-reach)

4. **Provider Engagement**
   - Share gap lists with providers
   - Offer point-of-care reminders
   - Provide incentives for gap closure

5. **Track and Measure**
   - Monitor gap closure rates weekly
   - Analyze which interventions work
   - Adjust strategy based on data

## Quality Improvement Target
**Goal:** Achieve and maintain 92%+ compliance rate across all measures
**Benefit:** Increased Stars rating → Higher member satisfaction and revenue
"""

# Upload document
volume_path = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"
dbutils.fs.put(f"{volume_path}/hedis_measures_guide.txt", hedis_measures_guide, overwrite=True)
print("✅ Uploaded: hedis_measures_guide.txt")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Knowledge Document 2: NCQA Quality Guidelines

# COMMAND ----------

ncqa_guidelines = """# NCQA Quality Guidelines for HEDIS Measures

## National Committee for Quality Assurance (NCQA)

NCQA is a private, non-profit organization dedicated to improving health care quality through measurement, transparency, and accountability.

## HEDIS Compliance Requirements

### Data Collection Methods

1. **Administrative Data (Claims)**
   - Preferred method
   - CPT/ICD codes submitted by providers
   - Pharmacy claims for medication adherence
   - Most cost-effective approach

2. **Medical Record Review (MRR)**
   - Used when administrative data insufficient
   - Manual chart review by trained abstractors
   - Supplemental to administrative data
   - More expensive but captures missing services

3. **Electronic Health Records (EHR)**
   - Direct integration with provider systems
   - Real-time data capture
   - Reduces lag time in reporting

### Continuous Enrollment Requirements

Members must be continuously enrolled during the measurement year to be included in the denominator.

**Allowable Gaps:**
- One gap up to 45 days during measurement year
- No gap during required lookback periods

**Exclusions:**
- Hospice enrollment
- Institutionalized members (for some measures)
- Medical reasons documented in chart

### Measurement Year vs. Reporting Year

- **Measurement Year:** Calendar year during which services occur (e.g., 2024)
- **Reporting Year:** Year when data is reported to NCQA (e.g., 2025)
- **Lag Time:** Typically 3-6 months for claims runout

### Audit Requirements

All HEDIS submissions are subject to NCQA audit:

1. **Annual Compliance Audit**
   - Validates data collection processes
   - Reviews medical records for accuracy
   - Confirms technical specifications followed

2. **Pass/Fail Criteria**
   - Must achieve ≥ 95% measure-level reportability
   - Bias must not exceed ±5 percentage points
   - Systems must meet NCQA standards

3. **Audit Preparation**
   - Document all processes
   - Train staff on specifications
   - Conduct internal pre-audits
   - Maintain audit trail

## Quality Improvement Strategies

### Population Health Management

1. **Risk Stratification**
   - Identify high-risk, high-gap members
   - Allocate resources to highest impact opportunities
   - Use predictive modeling for targeting

2. **Care Coordination**
   - Assign care managers to high-risk members
   - Coordinate between PCPs and specialists
   - Address social determinants of health
   - Medication therapy management

3. **Provider Partnerships**
   - Share quality dashboards with providers
   - Offer gap closure incentives
   - Provide EHR alerts at point of care
   - Collaborative quality improvement teams

### Member Engagement

1. **Outreach Campaigns**
   - Targeted mailings and phone calls
   - Culturally appropriate materials
   - Language translation services
   - Mobile health reminders

2. **Barriers Removal**
   - Transportation assistance
   - Extended clinic hours
   - Telehealth options
   - Reduced or waived copays

3. **Health Education**
   - Explain importance of preventive care
   - Share personalized health information
   - Wellness program incentives
   - Health literacy improvements

## Stars Rating Impact

### CMS Stars Methodology

HEDIS measures comprise approximately 60% of the Medicare Stars rating.

**Stars Distribution:**
- 5 Stars: 1 in 10 plans
- 4+ Stars: Quality bonus payments
- 3 Stars or below: Risk of CMS sanctions

**Financial Impact:**
- 5-Star plans: +5% premium bonus
- 4-Star plans: +3% premium bonus
- Higher member retention and enrollment

### High-Impact HEDIS Measures for Stars

1. **Diabetes Care (CDC)** - Triple-weighted
2. **Controlling High Blood Pressure (CBP)** - Triple-weighted
3. **Breast Cancer Screening (BCS)** - Double-weighted
4. **Colorectal Cancer Screening (COL)** - Double-weighted

**Strategy:** Prioritize triple- and double-weighted measures for maximum Stars impact.

## Compliance Best Practices

1. **Early Gap Identification**
   - Identify gaps by Q2 for intervention time
   - Use predictive analytics to forecast gaps
   - Monitor real-time vs. waiting for year-end

2. **Continuous Monitoring**
   - Weekly performance dashboards
   - Monthly provider scorecards
   - Quarterly trend analysis
   - Annual HEDIS reporting

3. **Cross-Functional Collaboration**
   - Clinical teams
   - Operations/IT
   - Provider network
   - Member services
   - Quality department

4. **Technology Enablement**
   - Automated gap identification
   - Member outreach tracking
   - EHR integration
   - Reporting automation

5. **Documentation Excellence**
   - Complete medical coding
   - Accurate diagnosis capture
   - Timely claims submission
   - Medical record completeness

## Common Pitfalls to Avoid

1. **Late Gap Identification** - Start outreach early in the year
2. **Incomplete Claims Data** - Work with providers on timely submission
3. **Poor Documentation** - Train providers on coding requirements
4. **Inadequate Follow-Up** - Multiple touch points increase success
5. **Lack of Member Engagement** - Use incentives and education

## Resources

- NCQA HEDIS Technical Specifications: www.ncqa.org/hedis
- CMS Stars Methodology: www.cms.gov/medicare/quality/stars
- Quality Compass Benchmarks: Available to NCQA members
"""

dbutils.fs.put(f"{volume_path}/ncqa_quality_guidelines.txt", ncqa_guidelines, overwrite=True)
print("✅ Uploaded: ncqa_quality_guidelines.txt")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Knowledge Document 3: Gap Closure Protocols

# COMMAND ----------

gap_closure_protocols = """# Gap Closure Protocols and Standard Operating Procedures

## Gap Closure Workflow

### Phase 1: Gap Identification (January-March)

**Step 1: Data Extraction**
- Extract eligible member population from enrollment system
- Identify measures applicable to each member based on age/gender/conditions
- Pull claims data for services received in prior year
- Flag members with missing services (gaps)

**Step 2: Gap Validation**
- Remove false positives (services not captured in claims)
- Apply exclusions (hospice, institutionalized, medical contraindications)
- Verify continuous enrollment criteria met
- Confirm member still active

**Step 3: Gap Prioritization**
- Calculate Stars impact score for each gap
- Assign priority level (High/Medium/Low)
- Consider member risk level
- Generate gap closure lists by intervention type

**Priority Matrix:**

| Risk Level | Measure Weight | Priority | Intervention |
|------------|---------------|----------|--------------|
| High       | Triple        | Critical | Care Manager |
| High       | Double/Single | High     | Care Manager |
| Medium     | Triple/Double | High     | Phone Outreach |
| Medium     | Single        | Medium   | Phone/Letter |
| Low        | Any           | Low      | Automated |

### Phase 2: Intervention (April-October)

**Critical Priority (Care Management)**
- Assign dedicated care manager
- Weekly member contact attempts
- Coordinate with PCP for appointments
- Arrange transportation if needed
- Follow up until gap closed or exhausted efforts
- Maximum 10 contact attempts

**High Priority (Intensive Outreach)**
- Phone call by quality nurse
- Follow-up call in 2 weeks if no response
- Letter sent after 2 failed call attempts
- Portal message (if member uses portal)
- Provider notification
- Maximum 5 contact attempts

**Medium Priority (Standard Outreach)**
- Initial phone call by health coach
- Follow-up letter after 2 weeks
- Portal message
- Maximum 3 contact attempts

**Low Priority (Automated)**
- Automated phone message
- Email or text reminder (if opted in)
- Mailed postcard
- Maximum 2 contact attempts

### Phase 3: Tracking and Validation (Ongoing)

**Weekly Monitoring**
- Pull updated claims data
- Identify newly closed gaps
- Update member gap status
- Generate intervention reports
- Adjust outreach strategy based on results

**Quality Validation**
- Verify service codes match measure requirements
- Confirm dates of service within measurement year
- Check for documentation of exclusions
- Flag any questionable claims for review

**Performance Metrics**
- Gap closure rate by measure
- Gap closure rate by intervention type
- Average time to close gap
- Cost per gap closed
- Return on investment

## Standard Phone Call Script

**Opening:**
"Hi [Member Name], this is [Caller Name] from [Health Plan] Quality Department. I'm calling about your preventive health care. Do you have a few minutes to talk?"

**Gap Explanation:**
"Our records show you're due for [Measure Name], which is [brief description]. This is an important preventive service that [benefit explanation]."

**Action Request:**
"Have you had this done recently? If so, we may not have received the claim yet. If not, I'd like to help you get it scheduled."

**Barrier Assessment:**
"Is there anything preventing you from getting this done? I can help with:"
- Finding a provider
- Scheduling an appointment
- Arranging transportation
- Understanding costs (usually $0 with insurance)

**Close:**
"I'll follow up with you in [timeframe] to see how it went. You can also call us at [number] if you have questions. Thank you for taking care of your health!"

**Documentation:**
- Call outcome (Reached/Left Message/Wrong Number/Declined)
- Member response and barriers identified
- Action taken (appointment scheduled, provider referral, etc.)
- Next follow-up date

## Medical Record Review Process

When administrative data is insufficient:

**Step 1: Provider Outreach**
- Request medical records for specific members
- Provide date range needed
- Explain measure requirements
- Offer secure upload portal

**Step 2: Chart Abstraction**
- Trained abstractor reviews chart
- Looks for service documentation
- Records findings in standardized format
- Flags unclear documentation

**Step 3: Validation**
- Second abstractor reviews sample
- Inter-rater reliability must be ≥95%
- Supervisor reviews all positive findings

**Step 4: Data Entry**
- Enter findings into HEDIS system
- Link to source documentation
- Apply to numerator if criteria met

## Gap Closure Incentives

### Member Incentives
- Gift card for completing preventive visit ($25-50)
- Health savings account credit
- Reduced premium (where allowed)
- Wellness program points
- Prize drawings

### Provider Incentives
- Quality bonuses tied to HEDIS performance
- Per-gap-closed payment ($50-100)
- Public recognition (top performers)
- Reduced administrative burden
- Data sharing and support

## Common Barriers and Solutions

| Barrier | Solution |
|---------|----------|
| Transportation | Arrange Uber/Lyft or taxi voucher |
| Cost concern | Explain $0 copay for preventive services |
| No PCP | Help find and schedule with in-network PCP |
| Language | Provide interpreter or translated materials |
| Health literacy | Use simple terms, pictures, examples |
| Distrust | Explain benefits, share testimonials |
| Too busy | Offer weekend/evening appointments |
| Forgot | Set up appointment reminders |

## Technology Tools

### Gap Identification
- SQL queries against claims database
- Natural language processing of medical records
- Predictive modeling for risk stratification

### Member Outreach
- Automated dialer for phone campaigns
- Email/SMS messaging platforms
- Member portal alerts
- Interactive voice response (IVR)

### Tracking and Reporting
- Gap closure dashboards (Power BI/Tableau)
- Provider scorecards
- Real-time performance monitoring
- Automated weekly reports

### EHR Integration
- Bi-directional data exchange (HL7/FHIR)
- Point-of-care gap alerts
- Quality measure documentation templates
- Batch claims submission

## Success Metrics

### Process Metrics
- % members reached by outreach attempts
- Average time from gap ID to first outreach
- % gaps assigned to intervention within 30 days
- % providers receiving gap lists quarterly

### Outcome Metrics
- Overall gap closure rate (Target: ≥75%)
- Gap closure rate by intervention type
- Gap closure rate by measure
- Year-over-year compliance rate improvement

### Financial Metrics
- Cost per gap closed
- ROI on gap closure programs
- Stars bonus payment increase
- Member retention improvement

## Annual Timeline

- **January:** Gap identification and validation
- **February:** Intervention planning and resource allocation
- **March-April:** High-priority outreach begins
- **May-August:** Peak intervention period
- **September-October:** Final push for remaining gaps
- **November-December:** Claims runout and final validation
- **Year-end:** HEDIS reporting to NCQA

## Continuous Improvement

1. **Monthly Review**
   - Analyze what's working vs. not working
   - Adjust intervention strategies
   - Reallocate resources to highest ROI activities

2. **Quarterly Deep Dive**
   - Compare to prior year same quarter
   - Benchmark against national averages
   - Identify new opportunities

3. **Annual Strategic Planning**
   - Set next year's goals
   - Budget for gap closure programs
   - Plan provider engagement
   - Enhance technology capabilities
"""

dbutils.fs.put(f"{volume_path}/gap_closure_protocols.txt", gap_closure_protocols, overwrite=True)
print("✅ Uploaded: gap_closure_protocols.txt")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Knowledge Document 4: Quality Team Communications

# COMMAND ----------

quality_communications = """# Quality Team Communications and FAQs

## Frequently Asked Questions

### General HEDIS Questions

**Q: What is HEDIS?**
A: HEDIS (Healthcare Effectiveness Data and Information Set) is a standardized set of performance measures developed by NCQA. It's used to compare health plan performance on important dimensions of care and service.

**Q: Why do HEDIS measures matter?**
A: HEDIS measures:
- Impact Medicare Stars ratings (and bonus payments)
- Reflect quality of care delivered to members
- Used by employers to choose health plans
- Required for NCQA accreditation
- Publicly reported on Medicare.gov

**Q: How many HEDIS measures are there?**
A: There are over 90 HEDIS measures across 6 domains:
1. Effectiveness of Care
2. Access/Availability of Care
3. Experience of Care
4. Utilization
5. Health Plan Descriptive Information
6. Measures Reported Using Electronic Clinical Data Systems

Our focus is on the ~15 highest-impact measures for Stars.

**Q: What's the difference between compliance rate and Stars rating?**
A: 
- Compliance rate = % of eligible members who received the service (our internal metric)
- Stars rating = How we compare to other health plans nationally (1-5 stars)
- A 92% compliance rate typically translates to 4.5-5 stars, depending on national benchmarks

### Gap Closure Questions

**Q: What is a "gap in care"?**
A: A gap in care means an eligible member has not received a required preventive service during the measurement year. For example, a 55-year-old woman who hasn't had a mammogram in the past 2 years has a BCS gap.

**Q: How often are gaps updated?**
A: Gaps are refreshed weekly as new claims data is processed. The dashboard always shows the most current gap status as of the last Sunday night refresh.

**Q: Can a gap be closed retroactively?**
A: Yes! If a member had the service but we didn't receive the claim, once the provider submits the claim (and it processes), the gap will automatically close in our next refresh. We also conduct medical record reviews to capture services not in claims data.

**Q: What's our gap closure rate target?**
A: Our target is ≥75% gap closure rate. This means if we identify 100 gaps at the start of the year, we aim to close at least 75 of them by year-end.

**Q: What happens if we can't close a gap?**
A: After exhausting all intervention attempts, we document the reason:
- Member declined service
- Unable to reach member
- Medical contraindication (becomes an exclusion)
- Member disenrolled

These members remain in our "unable to close" tracking for analysis and improvement planning.

### Dashboard Questions

**Q: How do I use the HEDIS Quality Dashboard?**
A:
1. **Overview Tab:** See high-level metrics and trends
2. **Measure Performance:** Drill into specific measures (BCS, CDC, etc.)
3. **Gap Analysis:** View open gaps by priority, measure, risk level
4. **Member Lookup:** Search for individual member gap details

**Q: What does the quality score represent?**
A: The quality score is an aggregate score (0-100) based on:
- Weighted average of all measure compliance rates
- Higher-impact measures weighted more heavily
- 85 = Good, 90 = Excellent, 92+ = Outstanding

**Q: How often is the dashboard updated?**
A: Real-time. The dashboard pulls live data from our Unity Catalog tables, which are refreshed weekly (Sunday nights) with the latest claims and enrollment data.

**Q: Can I export data from the dashboard?**
A: Yes! Most visualizations have an export button. You can download:
- Summary tables to CSV/Excel
- Charts as images (PNG)
- Full data extracts via SQL Warehouse

### Member Outreach Questions

**Q: How do I prioritize which members to contact first?**
A: Use the priority field in the Gap Analysis tab:
- **Critical:** High-risk members + triple-weighted measures → Care manager assignment
- **High:** High-risk OR double-weighted measures → Intensive phone outreach
- **Medium:** Standard outreach approach
- **Low:** Automated reminders

**Q: What if a member says they already had the service?**
A: 
1. Ask for details (provider name, approximate date)
2. Document the information
3. Follow up with the provider to request claim submission
4. Initiate medical record review if claim not found
5. Update member's gap status once confirmed

**Q: Can members refuse services?**
A: Yes. Members have the right to decline preventive services. We document the refusal and note:
- Date of refusal
- Reason given (if any)
- Educational information provided
- Member acknowledgment

The gap remains open but is flagged as "member declined" so we don't continue outreach.

**Q: What if a member has barriers (transportation, cost, etc.)?**
A: We offer:
- Transportation assistance (Uber/Lyft vouchers)
- Cost education ($0 copay for preventive services)
- Provider finding assistance
- Flexible appointment scheduling (evenings/weekends)
- Language interpretation services
- Health education materials

Document all barriers in the member's outreach notes so we can address them.

### Provider Engagement Questions

**Q: How do providers receive gap lists?**
A: We distribute gap lists to providers quarterly via:
- Secure provider portal
- Direct email to practice manager
- EHR integration (for participating providers)
- Monthly provider scorecard

**Q: Do providers get paid for closing gaps?**
A: Many providers have quality incentive contracts that include HEDIS performance bonuses. Check with Provider Network team for specific contract terms.

**Q: What if a provider says the service was completed but we show a gap?**
A: Common reasons:
1. Claim not yet processed (7-30 day lag)
2. Claim rejected/denied (billing error)
3. Wrong diagnosis/procedure code used
4. Service done out of network (we may not have visibility)

Solution: Request medical records for verification.

### Reporting Questions

**Q: When is HEDIS data reported to NCQA?**
A: Annually by June 30th for the prior calendar year. For example, 2024 measurement year data is reported by June 30, 2025.

**Q: What happens during a HEDIS audit?**
A: NCQA audits our HEDIS submission annually:
1. Reviews our processes and documentation
2. Validates a sample of medical records
3. Tests our data systems
4. Issues audit findings and certification

We must maintain ≥95% accuracy to pass.

**Q: Where can I see our performance vs. national benchmarks?**
A: In the dashboard "Measure Performance" tab, click "Show Benchmarks" to see:
- Our current rate
- National 50th percentile (average)
- National 75th percentile (above average)
- National 90th percentile (top performers)

### System/Technical Questions

**Q: Why is my data not showing up?**
A: Check:
1. Date range filter (top of dashboard)
2. Measure filter (may be filtered to specific measures)
3. Member population filter (active members only by default)
4. Data refresh date (bottom of page)

If still not appearing, contact IT support.

**Q: Can I create custom reports?**
A: Yes! The dashboard is built on our Unity Catalog data. You can:
1. Use the SQL Warehouse to write custom queries
2. Connect Power BI/Tableau to our tables
3. Request report development from Analytics team

**Q: Who has access to the HEDIS dashboard?**
A: Access is role-based:
- **Quality Team:** Full access (all members, all data)
- **Care Managers:** Access to assigned members only
- **Providers:** Access to their attributed members only
- **Executives:** Summary/aggregate views only

## Contact Information

**Quality Department:**
- Email: quality@healthplan.com
- Phone: (555) 123-4567
- Hours: Monday-Friday 8am-5pm

**Technical Support:**
- Email: itsupport@healthplan.com
- Phone: (555) 234-5678
- Hours: 24/7 for critical issues

**Provider Services:**
- Email: providerservices@healthplan.com
- Phone: (555) 345-6789
- Hours: Monday-Friday 8am-6pm

## Quick Reference: Measure Codes

| Code | Measure Name | Eligible Population |
|------|--------------|---------------------|
| BCS | Breast Cancer Screening | Women 50-74 |
| CDC | Comprehensive Diabetes Care | Adults 18-75 with diabetes |
| CBP | Controlling High Blood Pressure | Adults 18-85 with hypertension |
| COL | Colorectal Cancer Screening | Adults 50-75 |
| CIS | Childhood Immunization Status | Children age 2 |
| W15 | Well-Child Visits (First 15 Months) | Children <15 months |
| AWC | Adolescent Well-Care Visits | Adolescents 12-21 |
| PPC | Prenatal and Postpartum Care | Women with deliveries |

## Resources

- **HEDIS Specifications:** S:\\Quality\\HEDIS\\Technical_Specs
- **Training Materials:** Learning Management System (LMS)
- **Provider Gap Lists:** Provider Portal
- **Member Outreach Scripts:** S:\\Quality\\Outreach\\Scripts
- **Weekly Gap Reports:** Emailed every Monday morning

## Stay Informed

- **Weekly Quality Newsletter:** Sent every Monday
- **Monthly Quality Team Meeting:** First Tuesday, 10am
- **Quarterly Provider Collaboration:** Third Wednesday
- **Annual HEDIS Training:** October (for next measurement year)
"""

dbutils.fs.put(f"{volume_path}/quality_team_communications.txt", quality_communications, overwrite=True)
print("✅ Uploaded: quality_team_communications.txt")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Uploads

# COMMAND ----------

# List all files in volume
files = dbutils.fs.ls(volume_path)

print(f"\n✅ Knowledge documents uploaded to: {volume_path}\n")
print("Files:")
for file in files:
    print(f"  - {file.name} ({file.size:,} bytes)")

print("\n✅ Knowledge documents upload complete!")

