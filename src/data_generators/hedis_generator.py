"""
HEDIS Quality Measures Data Generator

Generates synthetic data for HEDIS quality measures including:
- Member eligibility and enrollment
- Clinical quality measures (BCS, CDC, CBP)
- Gap closure tracking
- Quality score trends (85% -> 92% improvement)
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from faker import Faker


class HEDISDataGenerator:
    """Generate synthetic HEDIS quality measures data"""
    
    def __init__(self, num_members: int = 10000, seed: int = 42):
        """
        Initialize generator
        
        Args:
            num_members: Number of members to generate
            seed: Random seed for reproducibility
        """
        self.num_members = num_members
        self.seed = seed
        random.seed(seed)
        self.fake = Faker()
        Faker.seed(seed)
        
        # HEDIS measures
        self.hedis_measures = {
            'BCS': 'Breast Cancer Screening',
            'CDC': 'Comprehensive Diabetes Care',
            'CBP': 'Controlling High Blood Pressure',
            'COL': 'Colorectal Cancer Screening',
            'CIS': 'Childhood Immunization Status',
            'W15': 'Well-Child Visits (First 15 Months)',
            'AWC': 'Adolescent Well-Care Visits',
            'PPC': 'Prenatal and Postpartum Care'
        }
        
        # Risk levels
        self.risk_levels = ['Low', 'Medium', 'High']
        
    def generate_members(self) -> List[Dict]:
        """Generate member eligibility and enrollment data"""
        members = []
        
        for i in range(1, self.num_members + 1):
            member_id = f"M{i:06d}"
            
            # Demographics
            gender = random.choice(['M', 'F'])
            age = random.randint(18, 85)
            
            # Enrollment
            enrollment_date = datetime.now() - timedelta(days=random.randint(365, 3650))
            is_active = random.random() > 0.05  # 95% active
            
            # Risk stratification
            risk_level = random.choices(
                self.risk_levels,
                weights=[0.6, 0.3, 0.1]  # 60% low, 30% medium, 10% high
            )[0]
            
            members.append({
                'member_id': member_id,
                'first_name': self.fake.first_name(),
                'last_name': self.fake.last_name(),
                'date_of_birth': (datetime.now() - timedelta(days=age*365)).date(),
                'age': age,
                'gender': gender,
                'enrollment_date': enrollment_date.date(),
                'is_active': is_active,
                'risk_level': risk_level,
                'address': self.fake.street_address(),
                'city': self.fake.city(),
                'state': self.fake.state_abbr(),
                'zip_code': self.fake.zipcode(),
                'phone': self.fake.phone_number(),
                'email': self.fake.email(),
                'created_at': datetime.now(),
                'source_system': 'ENROLLMENT_SYSTEM'
            })
        
        return members
    
    def generate_clinical_measures(self, members: List[Dict]) -> List[Dict]:
        """Generate clinical quality measures data"""
        measures = []
        
        # Create 2 years of historical data + current year
        current_year = datetime.now().year
        years = [current_year - 2, current_year - 1, current_year]
        
        for member in members:
            member_id = member['member_id']
            age = member['age']
            gender = member['gender']
            risk_level = member['risk_level']
            
            # Determine applicable measures based on age/gender
            applicable_measures = self._get_applicable_measures(age, gender)
            
            for year in years:
                # Base compliance rate increases over time (85% -> 90% -> 92%)
                if year == current_year - 2:
                    base_compliance = 0.85
                elif year == current_year - 1:
                    base_compliance = 0.90
                else:
                    base_compliance = 0.92
                
                # Adjust for risk level
                if risk_level == 'High':
                    compliance_modifier = -0.15
                elif risk_level == 'Medium':
                    compliance_modifier = -0.05
                else:
                    compliance_modifier = 0.05
                
                for measure_code in applicable_measures:
                    # Determine if compliant
                    compliance_probability = max(0.1, min(0.99, 
                        base_compliance + compliance_modifier))
                    is_compliant = random.random() < compliance_probability
                    
                    # Service date
                    if is_compliant:
                        service_date = datetime(year, random.randint(1, 12), 
                                              random.randint(1, 28))
                    else:
                        service_date = None
                    
                    # Gap in care
                    has_gap = not is_compliant
                    
                    # Gap closure (for non-current year gaps)
                    gap_closed = False
                    gap_closure_date = None
                    if has_gap and year < current_year:
                        # Some gaps get closed
                        gap_closed = random.random() < 0.70  # 70% gap closure rate
                        if gap_closed:
                            gap_closure_date = datetime(year, random.randint(1, 12), 
                                                       random.randint(1, 28))
                    
                    measures.append({
                        'measure_id': f"{measure_code}_{member_id}_{year}",
                        'member_id': member_id,
                        'measure_code': measure_code,
                        'measure_name': self.hedis_measures[measure_code],
                        'measurement_year': year,
                        'is_compliant': is_compliant,
                        'service_date': service_date,
                        'has_gap': has_gap,
                        'gap_closed': gap_closed,
                        'gap_closure_date': gap_closure_date,
                        'numerator': 1 if is_compliant else 0,
                        'denominator': 1,
                        'created_at': datetime.now(),
                        'source_system': 'CLINICAL_SYSTEM'
                    })
        
        return measures
    
    def generate_gap_tracking(self, measures: List[Dict]) -> List[Dict]:
        """Generate gap closure tracking data"""
        gaps = []
        gap_id = 1
        
        for measure in measures:
            if measure['has_gap']:
                # Determine intervention type
                intervention_type = random.choice([
                    'Phone Outreach',
                    'Letter Campaign',
                    'Provider Outreach',
                    'Care Coordinator',
                    'Patient Portal Message'
                ])
                
                # Number of attempts
                num_attempts = random.randint(1, 5) if measure['gap_closed'] else random.randint(1, 3)
                
                # Priority based on risk level and measure
                priority = self._calculate_gap_priority(
                    measure['measure_code'],
                    measure.get('member_risk_level', 'Medium')
                )
                
                gaps.append({
                    'gap_id': f"GAP{gap_id:08d}",
                    'member_id': measure['member_id'],
                    'measure_code': measure['measure_code'],
                    'measure_name': measure['measure_name'],
                    'measurement_year': measure['measurement_year'],
                    'identified_date': datetime(measure['measurement_year'], 1, 15),
                    'priority': priority,
                    'intervention_type': intervention_type,
                    'num_attempts': num_attempts,
                    'is_closed': measure['gap_closed'],
                    'closure_date': measure['gap_closure_date'],
                    'days_to_close': (measure['gap_closure_date'] - 
                                     datetime(measure['measurement_year'], 1, 15)).days 
                                     if measure['gap_closure_date'] else None,
                    'assigned_to': self.fake.name(),
                    'notes': self._generate_gap_notes(measure['gap_closed']),
                    'created_at': datetime.now(),
                    'source_system': 'GAP_CLOSURE_SYSTEM'
                })
                
                gap_id += 1
        
        return gaps
    
    def generate_quality_scores(self) -> List[Dict]:
        """Generate overall quality scores by year"""
        current_year = datetime.now().year
        scores = []
        
        # Historical trend showing improvement
        score_data = [
            (current_year - 2, 0.85, 85.0, 3.5),
            (current_year - 1, 0.90, 90.0, 4.0),
            (current_year, 0.92, 92.0, 4.5)
        ]
        
        for year, compliance_rate, quality_score, stars_rating in score_data:
            scores.append({
                'measurement_year': year,
                'overall_compliance_rate': compliance_rate,
                'quality_score': quality_score,
                'stars_rating': stars_rating,
                'total_measures': len(self.hedis_measures),
                'members_compliant': int(self.num_members * compliance_rate),
                'total_members': self.num_members,
                'gap_closure_rate': 0.65 if year == current_year - 2 else 
                                   (0.70 if year == current_year - 1 else 0.75),
                'ncqa_percentile': 60 if year == current_year - 2 else
                                  (75 if year == current_year - 1 else 85),
                'created_at': datetime.now()
            })
        
        return scores
    
    def _get_applicable_measures(self, age: int, gender: str) -> List[str]:
        """Determine which HEDIS measures apply to a member"""
        measures = []
        
        # BCS - Women 50-74
        if gender == 'F' and 50 <= age <= 74:
            measures.append('BCS')
        
        # CDC - Adults with diabetes (assume 25% have diabetes)
        if age >= 18 and random.random() < 0.25:
            measures.append('CDC')
        
        # CBP - Adults 18-85 with hypertension (assume 35% have HTN)
        if 18 <= age <= 85 and random.random() < 0.35:
            measures.append('CBP')
        
        # COL - Adults 50-75
        if 50 <= age <= 75:
            measures.append('COL')
        
        # CIS - Children age 2
        if age == 2:
            measures.append('CIS')
        
        # W15 - Children under 15 months (represented as age 1)
        if age == 1:
            measures.append('W15')
        
        # AWC - Adolescents 12-21
        if 12 <= age <= 21:
            measures.append('AWC')
        
        # PPC - Women of childbearing age (assume 10% pregnant)
        if gender == 'F' and 15 <= age <= 44 and random.random() < 0.10:
            measures.append('PPC')
        
        return measures
    
    def _calculate_gap_priority(self, measure_code: str, risk_level: str) -> str:
        """Calculate gap priority"""
        high_impact_measures = ['CDC', 'CBP', 'BCS']
        
        if risk_level == 'High':
            return 'High'
        elif measure_code in high_impact_measures:
            return 'High' if risk_level == 'Medium' else 'Medium'
        else:
            return 'Low'
    
    def _generate_gap_notes(self, is_closed: bool) -> str:
        """Generate gap closure notes"""
        if is_closed:
            return random.choice([
                'Member completed screening at annual wellness visit',
                'Provider confirmed service completed, updating records',
                'Member scheduled and completed required service',
                'Claims data updated to reflect completed service'
            ])
        else:
            return random.choice([
                'Attempted outreach, no response',
                'Member declined service',
                'Waiting for appointment scheduled',
                'Provider coordination in progress'
            ])

