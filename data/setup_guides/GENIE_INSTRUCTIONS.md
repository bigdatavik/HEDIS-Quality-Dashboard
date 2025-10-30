# Genie Space - Instructions Tab Content

## Copy-Paste This Into Genie "Instructions" Tab

---

### 📝 General Instructions (Text Tab):

```
Examples:
* "HEDIS" stands for Healthcare Effectiveness Data and Information Set
* BCS = Breast Cancer Screening, CDC = Comprehensive Diabetes Care, CBP = Controlling Blood Pressure, COL = Colorectal Cancer Screening, OMW = Osteoporosis Management in Women
* Member IDs are in format M000001, M000002, M000003, etc. (always 7 characters: M plus 6 digits)
* Measure codes use standard HEDIS abbreviations (BCS, CDC, CBP, COL, OMW)
* Compliance rate is calculated as: (members_compliant / total_eligible_members) * 100
* Gap in care means a member is eligible for a measure but has not completed the required screening/test
* Quality score ranges from 0-100%, where higher is better
* Star rating ranges from 1-5 stars based on compliance thresholds (5 stars = ≥90%, 4 stars = 80-89%, 3 stars = 70-79%)
* When a user asks for performance, show compliance rate percentage
* When a user asks about gaps, show count of members with open gaps
* Always include the measurement period (year) in results
* High-weight measures (CDC, CBP, COL) have 3x impact on star rating
* Medium-weight measures (BCS, OMW) have 2x impact on star rating
* Eligible members count can change as members enroll, disenroll, age, or get new diagnoses

(You can use markdown text)
```

---

### 📝 SQL Expressions (SQL Expressions Tab):

**Note:** Add these as separate examples in the SQL Expressions tab. Each example should be added individually.

---

**Example 1: Calculate compliance rate by measure**
```sql
SELECT 
  measure_code,
  COUNT(DISTINCT CASE WHEN is_compliant THEN member_id END) * 100.0 / 
  COUNT(DISTINCT member_id) as compliance_rate_pct,
  COUNT(DISTINCT member_id) as total_eligible,
  COUNT(DISTINCT CASE WHEN is_compliant THEN member_id END) as compliant_count,
  COUNT(DISTINCT CASE WHEN NOT is_compliant THEN member_id END) as gap_count
FROM humana_quality.hedis_gold.member_measures
GROUP BY measure_code
ORDER BY compliance_rate_pct DESC
```

---

**Example 2: Find open gaps by measure**
```sql
SELECT 
  member_id, 
  measure_code, 
  measure_name,
  gap_closure_action,
  days_until_due
FROM humana_quality.hedis_gold.member_measures
WHERE is_compliant = FALSE
ORDER BY days_until_due ASC
```

---

**Example 3: Top performing measures**
```sql
SELECT 
  measure_code,
  measure_name,
  compliance_rate_pct,
  star_rating,
  trend
FROM humana_quality.hedis_gold.measure_performance
ORDER BY compliance_rate_pct DESC
LIMIT 10
```

---

**Example 4: Members with multiple gaps**
```sql
SELECT 
  member_id,
  COUNT(*) as gap_count,
  COLLECT_SET(measure_code) as gap_measures
FROM humana_quality.hedis_gold.member_measures
WHERE is_compliant = FALSE
GROUP BY member_id
HAVING COUNT(*) >= 2
ORDER BY gap_count DESC
```

---

**Example 5: Compliance trend by month**
```sql
SELECT 
  measure_code,
  DATE_TRUNC('month', last_updated) as month,
  COUNT(DISTINCT CASE WHEN is_compliant THEN member_id END) * 100.0 / 
  COUNT(DISTINCT member_id) as compliance_rate_pct
FROM humana_quality.hedis_gold.member_measures
GROUP BY measure_code, DATE_TRUNC('month', last_updated)
ORDER BY measure_code, month
```

---

**Example 6: Star rating projection**
```sql
SELECT 
  SUM(compliance_rate_pct * measure_weight) / SUM(measure_weight) as weighted_avg_compliance,
  CASE
    WHEN SUM(compliance_rate_pct * measure_weight) / SUM(measure_weight) >= 90 THEN 5
    WHEN SUM(compliance_rate_pct * measure_weight) / SUM(measure_weight) >= 80 THEN 4
    WHEN SUM(compliance_rate_pct * measure_weight) / SUM(measure_weight) >= 70 THEN 3
    WHEN SUM(compliance_rate_pct * measure_weight) / SUM(measure_weight) >= 60 THEN 2
    ELSE 1
  END as projected_star_rating
FROM humana_quality.hedis_gold.measure_performance
```

---

**Example 7: Revenue opportunity by measure**
```sql
SELECT 
  measure_code,
  gap_members as members_with_gaps,
  CASE 
    WHEN measure_code IN ('CDC', 'CBP', 'COL') THEN gap_members * 150
    WHEN measure_code IN ('BCS', 'OMW') THEN gap_members * 100
    ELSE gap_members * 50
  END as estimated_revenue_opportunity
FROM humana_quality.hedis_gold.measure_performance
ORDER BY estimated_revenue_opportunity DESC
```

---

**Example 8: High-priority gaps (closing soon)**
```sql
SELECT 
  member_id,
  measure_code,
  measure_name,
  gap_closure_action,
  days_until_due,
  CASE 
    WHEN measure_code IN ('CDC', 'CBP', 'COL') THEN 'High Impact'
    WHEN measure_code IN ('BCS', 'OMW') THEN 'Medium Impact'
    ELSE 'Standard Impact'
  END as measure_priority
FROM humana_quality.hedis_gold.member_measures
WHERE is_compliant = FALSE
  AND days_until_due <= 90
ORDER BY days_until_due ASC, measure_priority DESC
```

---

## 📋 After Adding Instructions:

1. Test Genie with sample queries:
   - "What is our overall compliance rate?"
   - "Show me BCS performance"
   - "Which members have CDC gaps?"
   - "Compare compliance rates across all measures"

2. Verify Genie understands:
   - Measure code abbreviations (BCS, CDC, etc.)
   - Member ID format (M000001)
   - Compliance rate calculation
   - Gap terminology

3. Copy the **Genie Space ID** from the URL:
   - Format: `01f06a3068a81406a386e8eaefc74545`
   - Found in URL: `.../genie/spaces/[SPACE_ID]`
   - Save for MCP integration

---

## ✅ Tips for Using Genie:

1. **Start broad, then narrow**: 
   - First: "Show me overall quality performance"
   - Then: "Show me only BCS performance"
   - Finally: "Show me BCS gaps for members under 60"

2. **Use natural language**:
   - Good: "What's our average compliance rate?"
   - Good: "Show me members with diabetes gaps"
   - Avoid: Complex SQL in natural language queries

3. **Leverage examples**:
   - Genie learns from the SQL examples you provided
   - Reference similar patterns to what you taught it

4. **Iterate on queries**:
   - If result isn't what you expected, rephrase
   - Add filters or constraints to narrow results
   - Ask follow-up questions to refine

---

## 🔍 Example Queries to Test:

**Aggregate Queries:**
- "What is our overall compliance rate?"
- "Show me compliance rates by measure"
- "How many gaps do we have for each measure?"
- "What's our projected star rating?"

**Comparison Queries:**
- "Compare BCS vs CDC performance"
- "Show me measures above 80% compliance"
- "Which measures improved this quarter?"

**Trending Queries:**
- "Show me compliance trend for BCS over the last 6 months"
- "How many gaps closed this month vs last month?"
- "What's our trend in overall compliance?"

**Cohort Queries:**
- "Which members have multiple gaps?"
- "Show me high-priority gaps closing in the next 60 days"
- "Find members with CDC gaps"

**Revenue Queries:**
- "What's the revenue opportunity by measure?"
- "Show me revenue impact of improving to 4 stars"
- "Calculate potential revenue from closing all CDC gaps"

