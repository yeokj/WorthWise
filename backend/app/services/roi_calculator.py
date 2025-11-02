"""
ROI Calculator Service
Core business logic for ROI, debt, earnings, and financial comfort calculations
"""

from typing import Dict, Any, Optional, Tuple
import math


class ROICalculator:
    """
    Calculate Return on Investment and related financial metrics
    for college education scenarios
    """
    
    # Default assumptions
    DEFAULT_PROGRAM_YEARS = 4
    DEFAULT_FOOD_MONTHLY = 0
    DEFAULT_TRANSPORT_MONTHLY = 0
    DEFAULT_BOOKS_ANNUAL = 0
    DEFAULT_MISC_MONTHLY = 0
    DEFAULT_UTILITIES_MONTHLY = 0
    
    def __init__(self):
        """Initialize ROI Calculator"""
        pass
    
    def calculate_total_cost(
        self,
        tuition_annual: int,
        housing_annual: int,
        food_monthly: int,
        transport_monthly: int,
        utilities_monthly: int,
        misc_monthly: int,
        books_annual: int
    ) -> Tuple[int, int, int]:
        """
        Calculate total annual cost
        
        Returns:
            Tuple of (true_yearly_cost, housing_annual, other_expenses)
        """
        food_annual = food_monthly * 12
        transport_annual = transport_monthly * 12
        utilities_annual = utilities_monthly * 12
        misc_annual = misc_monthly * 12
        
        other_expenses = (
            food_annual +
            transport_annual +
            utilities_annual +
            misc_annual +
            books_annual
        )
        
        true_yearly_cost = tuition_annual + housing_annual + other_expenses
        
        return true_yearly_cost, housing_annual, other_expenses
    
    def calculate_debt(
        self,
        yearly_cost: int,
        aid_annual: int,
        cash_annual: int,
        program_years: int,
        loan_apr: float
    ) -> int:
        """
        Calculate expected debt at graduation
        
        Debt accumulates with compound interest each year
        
        Args:
            yearly_cost: Annual total cost
            aid_annual: Annual grants/scholarships (non-repayable)
            cash_annual: Annual cash contribution
            program_years: Number of years in program
            loan_apr: Annual loan interest rate
            
        Returns:
            Total debt at graduation
        """
        # Annual amount that needs to be borrowed
        annual_need = max(0, yearly_cost - aid_annual - cash_annual)
        
        if annual_need == 0:
            return 0
        
        # Calculate debt with compound interest
        # Loans taken in year 1 accrue interest for (n-1) years, year 2 for (n-2) years, etc.
        total_debt = 0
        for year in range(program_years):
            years_accumulating = program_years - year - 1
            loan_with_interest = annual_need * math.pow(1 + loan_apr, years_accumulating)
            total_debt += loan_with_interest
        
        return int(total_debt)
    
    def calculate_roi(
        self,
        total_investment: int,
        earnings_year_5: Optional[int],
        earnings_year_10: Optional[int] = None
    ) -> Optional[float]:
        """
        Calculate Return on Investment
        
        ROI = (Cumulative Earnings - Total Investment) / Total Investment
        
        Args:
            total_investment: Total cost of education (debt + cash + aid)
            earnings_year_5: Earnings 5 years after graduation
            earnings_year_10: Earnings 10 years after graduation (optional)
            
        Returns:
            ROI ratio or None if insufficient data
        """
        if not earnings_year_5 or total_investment <= 0:
            return None
        
        # Use 5-year earnings as proxy for earning potential
        # Simplified: assume linear growth to year 5, then stable
        # More sophisticated: use present value of future earnings
        cumulative_earnings = earnings_year_5 * 5  # Simplified
        
        roi = (cumulative_earnings - total_investment) / total_investment
        
        return round(roi, 2)
    
    def calculate_payback_period(
        self,
        total_debt: int,
        earnings_year_1: Optional[int],
        effective_tax_rate: float,
        living_expenses_annual: int = 30000
    ) -> Optional[float]:
        """
        Calculate debt payback period in years
        
        Assumes disposable income after taxes and living expenses
        goes toward debt repayment
        
        Args:
            total_debt: Total debt at graduation
            earnings_year_1: First year earnings
            effective_tax_rate: Tax rate (decimal)
            living_expenses_annual: Annual living expenses
            
        Returns:
            Years to payback or None if cannot payback
        """
        if not earnings_year_1 or total_debt <= 0:
            return None
        
        # Calculate disposable income
        after_tax_income = earnings_year_1 * (1 - effective_tax_rate)
        disposable_income = after_tax_income - living_expenses_annual
        
        if disposable_income <= 0:
            return None  # Cannot afford to pay back
        
        # Simple calculation: debt / annual_payment
        # More sophisticated would account for interest during repayment
        payback_years = total_debt / disposable_income
        
        return round(payback_years, 1)
    
    def calculate_dti(
        self,
        total_debt: int,
        earnings_year_1: Optional[int]
    ) -> Optional[float]:
        """
        Calculate Debt-to-Income ratio for year 1
        
        DTI = Total Debt / Annual Income
        
        Args:
            total_debt: Total debt at graduation
            earnings_year_1: First year earnings
            
        Returns:
            DTI ratio or None if no earnings data
        """
        if not earnings_year_1 or earnings_year_1 <= 0:
            return None
        
        dti = total_debt / earnings_year_1
        
        return round(dti, 2)
    
    def calculate_comfort_index(
        self,
        earnings_year_1: Optional[int],
        total_debt: int,
        dti: Optional[float],
        graduation_rate: Optional[float]
    ) -> Optional[float]:
        """
        Calculate financial comfort index (0-100)
        
        Higher is better. Considers:
        - Earnings level
        - Debt burden
        - Graduation likelihood
        
        Args:
            earnings_year_1: First year earnings
            total_debt: Total debt at graduation
            dti: Debt-to-income ratio
            graduation_rate: Graduation rate (0-1)
            
        Returns:
            Comfort index (0-100) or None
        """
        if not earnings_year_1:
            return None
        
        # Earnings score (0-40 points)
        # $50K = 20 points, $100K+ = 40 points
        earnings_score = min(40, (earnings_year_1 / 100000) * 40)
        
        # Debt score (0-30 points, inverse)
        # DTI < 0.5 = 30 points, DTI > 2.0 = 0 points
        if dti is not None:
            if dti <= 0.5:
                debt_score = 30
            elif dti >= 2.0:
                debt_score = 0
            else:
                debt_score = 30 * (1 - (dti - 0.5) / 1.5)
        else:
            debt_score = 15  # Neutral if no debt data
        
        # Graduation rate score (0-30 points)
        if graduation_rate is not None:
            grad_score = graduation_rate * 30
        else:
            grad_score = 15  # Neutral if no data
        
        comfort_index = earnings_score + debt_score + grad_score
        
        return round(comfort_index, 1)
    
    def apply_regional_adjustment(
        self,
        salary: int,
        rpp_index: Optional[float]
    ) -> int:
        """
        Adjust salary for regional cost of living
        
        Args:
            salary: Nominal salary
            rpp_index: Regional Price Parity index (100 = national average)
            
        Returns:
            Adjusted salary
        """
        if rpp_index is None or rpp_index == 0:
            return salary
        
        # Convert to purchasing power equivalent
        adjusted = salary / (rpp_index / 100)
        
        return int(adjusted)
    
    def calculate_housing_cost(
        self,
        fmr_monthly: int,
        roommate_count: int
    ) -> int:
        """
        Calculate annual housing cost adjusted for roommates
        
        Args:
            fmr_monthly: Fair Market Rent monthly
            roommate_count: Number of roommates
            
        Returns:
            Annual housing cost
        """
        # Split rent among roommates + self
        monthly_share = fmr_monthly / (roommate_count + 1)
        annual_cost = int(monthly_share * 12)
        
        return annual_cost
    
    def get_default_values(self) -> Dict[str, Any]:
        """
        Get default assumption values
        
        Returns:
            Dictionary of default values
        """
        return {
            "program_years": self.DEFAULT_PROGRAM_YEARS,
            "food_monthly": self.DEFAULT_FOOD_MONTHLY,
            "transport_monthly": self.DEFAULT_TRANSPORT_MONTHLY,
            "books_annual": self.DEFAULT_BOOKS_ANNUAL,
            "misc_monthly": self.DEFAULT_MISC_MONTHLY,
            "utilities_monthly": self.DEFAULT_UTILITIES_MONTHLY
        }

