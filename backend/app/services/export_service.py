"""
Export Service
Generate CSV exports for scenarios and comparisons
"""

import csv
import io
from typing import List
from fastapi.responses import StreamingResponse

from app.schemas.compute import ComputeResponse, KPIResult
from app.schemas.compare import CompareResponse


class ExportService:
    """Service for exporting data to CSV format"""
    
    @staticmethod
    def generate_scenario_csv(response: ComputeResponse) -> StreamingResponse:
        """
        Generate CSV for a single scenario
        
        Args:
            response: ComputeResponse object
            
        Returns:
            StreamingResponse with CSV file
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["Metric", "Value"])
        writer.writerow([])
        
        # Scenario parameters
        writer.writerow(["SCENARIO PARAMETERS", ""])
        writer.writerow(["Institution ID", response.scenario.institution_id])
        writer.writerow(["CIP Code", response.scenario.cip_code])
        writer.writerow(["Housing Type", response.scenario.housing_type])
        writer.writerow(["Roommates", response.scenario.roommate_count])
        writer.writerow(["Annual Aid", f"${response.scenario.aid_annual:,}"])
        writer.writerow(["Annual Cash", f"${response.scenario.cash_annual:,}"])
        writer.writerow(["Loan APR", f"{response.scenario.loan_apr:.2%}"])
        writer.writerow([])
        
        # KPIs
        writer.writerow(["KEY PERFORMANCE INDICATORS", ""])
        kpis = response.kpis
        writer.writerow(["True Yearly Cost", f"${kpis.true_yearly_cost:,}"])
        writer.writerow(["Tuition & Fees", f"${kpis.tuition_fees:,}"])
        writer.writerow(["Housing (Annual)", f"${kpis.housing_annual:,}"])
        writer.writerow(["Other Expenses", f"${kpis.other_expenses:,}"])
        writer.writerow(["Expected Debt at Graduation", f"${kpis.expected_debt_at_grad:,}"])
        
        if kpis.earnings_year_1:
            writer.writerow(["Earnings Year 1", f"${kpis.earnings_year_1:,}"])
        if kpis.earnings_year_3:
            writer.writerow(["Earnings Year 3", f"${kpis.earnings_year_3:,}"])
        if kpis.earnings_year_5:
            writer.writerow(["Earnings Year 5", f"${kpis.earnings_year_5:,}"])
        
        if kpis.roi is not None:
            writer.writerow(["ROI", f"{kpis.roi:.2f}"])
        if kpis.payback_years is not None:
            writer.writerow(["Payback Period (years)", f"{kpis.payback_years:.1f}"])
        if kpis.dti_year_1 is not None:
            writer.writerow(["DTI Year 1", f"{kpis.dti_year_1:.2f}"])
        if kpis.graduation_rate is not None:
            writer.writerow(["Graduation Rate", f"{kpis.graduation_rate:.1%}"])
        if kpis.comfort_index is not None:
            writer.writerow(["Comfort Index", f"{kpis.comfort_index:.1f}"])
        
        writer.writerow([])
        
        # Warnings
        if response.warnings:
            writer.writerow(["WARNINGS", ""])
            for warning in response.warnings:
                writer.writerow(["", warning])
        
        # Reset string buffer position
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=scenario_export.csv"
            }
        )
    
    @staticmethod
    def generate_comparison_csv(response: CompareResponse) -> StreamingResponse:
        """
        Generate CSV for scenario comparison
        
        Args:
            response: CompareResponse object
            
        Returns:
            StreamingResponse with CSV file
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header row
        headers = ["Metric"]
        for idx, comp in enumerate(response.comparisons):
            headers.append(f"Scenario {idx + 1}: {comp.institution_name}")
        writer.writerow(headers)
        writer.writerow([])
        
        # Cost metrics
        writer.writerow(["COSTS", ""])
        ExportService._write_comparison_row(
            writer, "True Yearly Cost",
            [c.kpis.true_yearly_cost for c in response.comparisons]
        )
        ExportService._write_comparison_row(
            writer, "Tuition & Fees",
            [c.kpis.tuition_fees for c in response.comparisons]
        )
        ExportService._write_comparison_row(
            writer, "Housing (Annual)",
            [c.kpis.housing_annual for c in response.comparisons]
        )
        ExportService._write_comparison_row(
            writer, "Other Expenses",
            [c.kpis.other_expenses for c in response.comparisons]
        )
        writer.writerow([])
        
        # Debt metrics
        writer.writerow(["DEBT", ""])
        ExportService._write_comparison_row(
            writer, "Expected Debt at Grad",
            [c.kpis.expected_debt_at_grad for c in response.comparisons]
        )
        writer.writerow([])
        
        # Earnings
        writer.writerow(["EARNINGS", ""])
        ExportService._write_comparison_row(
            writer, "Year 1 Earnings",
            [c.kpis.earnings_year_1 for c in response.comparisons]
        )
        ExportService._write_comparison_row(
            writer, "Year 3 Earnings",
            [c.kpis.earnings_year_3 for c in response.comparisons]
        )
        ExportService._write_comparison_row(
            writer, "Year 5 Earnings",
            [c.kpis.earnings_year_5 for c in response.comparisons]
        )
        writer.writerow([])
        
        # ROI metrics
        writer.writerow(["ROI METRICS", ""])
        ExportService._write_comparison_row(
            writer, "ROI",
            [c.kpis.roi for c in response.comparisons],
            formatter=lambda x: f"{x:.2f}" if x else "N/A"
        )
        ExportService._write_comparison_row(
            writer, "Payback Years",
            [c.kpis.payback_years for c in response.comparisons],
            formatter=lambda x: f"{x:.1f}" if x else "N/A"
        )
        ExportService._write_comparison_row(
            writer, "DTI Year 1",
            [c.kpis.dti_year_1 for c in response.comparisons],
            formatter=lambda x: f"{x:.2f}" if x else "N/A"
        )
        ExportService._write_comparison_row(
            writer, "Graduation Rate",
            [c.kpis.graduation_rate for c in response.comparisons],
            formatter=lambda x: f"{x:.1%}" if x else "N/A"
        )
        ExportService._write_comparison_row(
            writer, "Comfort Index",
            [c.kpis.comfort_index for c in response.comparisons],
            formatter=lambda x: f"{x:.1f}" if x else "N/A"
        )
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=comparison_export.csv"
            }
        )
    
    @staticmethod
    def _write_comparison_row(
        writer: csv.writer,
        label: str,
        values: List,
        formatter=None
    ):
        """Helper to write a comparison row"""
        row = [label]
        for value in values:
            if formatter:
                row.append(formatter(value))
            elif value is None:
                row.append("N/A")
            elif isinstance(value, (int, float)):
                row.append(f"${value:,}" if isinstance(value, int) else f"{value:.2f}")
            else:
                row.append(str(value))
        writer.writerow(row)

