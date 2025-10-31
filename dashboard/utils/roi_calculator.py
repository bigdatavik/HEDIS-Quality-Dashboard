"""
ROI Calculator Utilities
Functions for calculating return on investment for gap closure initiatives
"""

def calculate_star_rating_bonus(current_members: int, current_star: float, target_star: float, 
                                 avg_revenue_per_member_monthly: float = 1500) -> dict:
    """
    Calculate quality bonus payment impact from Star Rating improvement
    
    Args:
        current_members: Number of members in plan
        current_star: Current star rating (e.g., 3.5)
        target_star: Target star rating (e.g., 4.0)
        avg_revenue_per_member_monthly: Average CMS payment per member per month
    
    Returns:
        Dict with bonus calculations
    """
    # Annual revenue
    annual_revenue = current_members * avg_revenue_per_member_monthly * 12
    
    # Bonus rates
    current_bonus_rate = 0.05 if current_star >= 4.0 else 0.0
    target_bonus_rate = 0.05 if target_star >= 4.0 else 0.0
    
    # Current and target bonus
    current_bonus = annual_revenue * current_bonus_rate
    target_bonus = annual_revenue * target_bonus_rate
    
    # Gain/loss
    bonus_gain = target_bonus - current_bonus
    
    return {
        'annual_revenue': annual_revenue,
        'current_bonus_rate': current_bonus_rate,
        'target_bonus_rate': target_bonus_rate,
        'current_bonus': current_bonus,
        'target_bonus': target_bonus,
        'bonus_gain': bonus_gain,
        'bonus_gain_monthly': bonus_gain / 12
    }


def calculate_gap_closure_roi(
    initiative_budget: float,
    target_gaps: int,
    expected_closure_rate: float,
    avg_cost_per_preventable_event: float = 8000,
    prevention_rate: float = 0.50,
    star_rating_bonus: float = 0,
) -> dict:
    """
    Calculate ROI for gap closure initiative
    
    Args:
        initiative_budget: Total budget for initiative
        target_gaps: Number of gaps targeted
        expected_closure_rate: Expected % of gaps that will be closed (0-1)
        avg_cost_per_preventable_event: Average cost of preventable ER/hospitalization
        prevention_rate: % of closed gaps that prevent an event (0-1)
        star_rating_bonus: Annual bonus gain from Star Rating improvement
    
    Returns:
        Dict with ROI calculations
    """
    # Gaps closed
    gaps_closed = int(target_gaps * expected_closure_rate)
    
    # Cost per gap
    cost_per_gap_closed = initiative_budget / gaps_closed if gaps_closed > 0 else 0
    
    # Avoided medical costs (Year 1)
    events_prevented = gaps_closed * prevention_rate
    avoided_costs_year1 = events_prevented * avg_cost_per_preventable_event
    
    # Total value Year 1
    total_value_year1 = avoided_costs_year1
    
    # Total value Year 2+ (annual)
    total_value_annual = avoided_costs_year1 + star_rating_bonus
    
    # 3-year total value
    total_value_3yr = total_value_year1 + (total_value_annual * 2)
    
    # ROI calculations
    roi_year1 = ((total_value_year1 - initiative_budget) / initiative_budget * 100) if initiative_budget > 0 else 0
    roi_3yr = ((total_value_3yr - initiative_budget) / initiative_budget * 100) if initiative_budget > 0 else 0
    
    # Payback period (months)
    payback_months = (initiative_budget / (total_value_annual / 12)) if total_value_annual > 0 else 999
    
    return {
        'initiative_budget': initiative_budget,
        'target_gaps': target_gaps,
        'expected_closure_rate': expected_closure_rate,
        'gaps_closed': gaps_closed,
        'cost_per_gap_closed': cost_per_gap_closed,
        'events_prevented': events_prevented,
        'avoided_costs_year1': avoided_costs_year1,
        'star_rating_bonus_annual': star_rating_bonus,
        'total_value_year1': total_value_year1,
        'total_value_annual': total_value_annual,
        'total_value_3yr': total_value_3yr,
        'roi_year1_pct': roi_year1,
        'roi_3yr_pct': roi_3yr,
        'payback_months': payback_months,
        'net_value_3yr': total_value_3yr - initiative_budget
    }


def format_currency(value: float) -> str:
    """Format value as currency"""
    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value/1_000:.1f}K"
    else:
        return f"${value:,.0f}"


def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value:.1f}%"

