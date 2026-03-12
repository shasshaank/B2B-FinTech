"""
Schema mapper service — provides default extraction schemas per document type.
"""
import json
from typing import Dict, Any, List

# Default extraction schemas per document category
DEFAULT_SCHEMAS: Dict[str, List[Dict[str, Any]]] = {
    "ALM (Asset-Liability Management)": [
        {"field_name": "maturity_bucket", "field_type": "string", "required": True, "description": "Time bucket (e.g., 1-7 days, 8-14 days, 1-3 months)"},
        {"field_name": "assets_amount", "field_type": "currency", "required": True, "description": "Total assets in this maturity bucket (₹ Cr)"},
        {"field_name": "liabilities_amount", "field_type": "currency", "required": True, "description": "Total liabilities in this maturity bucket (₹ Cr)"},
        {"field_name": "gap", "field_type": "currency", "required": True, "description": "Gap = Assets - Liabilities (₹ Cr)"},
        {"field_name": "cumulative_gap", "field_type": "currency", "required": False, "description": "Running cumulative gap (₹ Cr)"},
    ],
    "Shareholding Pattern": [
        {"field_name": "shareholder_name", "field_type": "string", "required": True, "description": "Name of the shareholder"},
        {"field_name": "holding_percentage", "field_type": "number", "required": True, "description": "Percentage of total shares held"},
        {"field_name": "share_count", "field_type": "number", "required": False, "description": "Number of shares held"},
        {"field_name": "shareholder_category", "field_type": "string", "required": False, "description": "Category: Promoter, Public, FII, DII, etc."},
    ],
    "Borrowing Profile": [
        {"field_name": "lender_name", "field_type": "string", "required": True, "description": "Name of the lending institution"},
        {"field_name": "facility_type", "field_type": "string", "required": True, "description": "Type of facility: Term Loan, CC, OD, etc."},
        {"field_name": "sanctioned_amount", "field_type": "currency", "required": True, "description": "Sanctioned facility amount (₹ Cr)"},
        {"field_name": "outstanding_amount", "field_type": "currency", "required": True, "description": "Current outstanding balance (₹ Cr)"},
        {"field_name": "interest_rate", "field_type": "number", "required": False, "description": "Interest rate (%)"},
        {"field_name": "maturity_date", "field_type": "date", "required": False, "description": "Loan maturity / expiry date"},
    ],
    "Annual Report - Profit & Loss": [
        {"field_name": "line_item", "field_type": "string", "required": True, "description": "P&L line item name"},
        {"field_name": "fy_current", "field_type": "currency", "required": True, "description": "Current financial year amount (₹ Cr)"},
        {"field_name": "fy_previous", "field_type": "currency", "required": False, "description": "Previous financial year amount (₹ Cr)"},
        {"field_name": "fy_two_years_ago", "field_type": "currency", "required": False, "description": "Two years ago financial year amount (₹ Cr)"},
    ],
    "Annual Report - Balance Sheet": [
        {"field_name": "line_item", "field_type": "string", "required": True, "description": "Balance sheet line item name"},
        {"field_name": "fy_current", "field_type": "currency", "required": True, "description": "Current financial year amount (₹ Cr)"},
        {"field_name": "fy_previous", "field_type": "currency", "required": False, "description": "Previous financial year amount (₹ Cr)"},
        {"field_name": "fy_two_years_ago", "field_type": "currency", "required": False, "description": "Two years ago financial year amount (₹ Cr)"},
    ],
    "Annual Report - Cash Flow": [
        {"field_name": "line_item", "field_type": "string", "required": True, "description": "Cash flow line item name"},
        {"field_name": "fy_current", "field_type": "currency", "required": True, "description": "Current financial year amount (₹ Cr)"},
        {"field_name": "fy_previous", "field_type": "currency", "required": False, "description": "Previous financial year amount (₹ Cr)"},
        {"field_name": "fy_two_years_ago", "field_type": "currency", "required": False, "description": "Two years ago financial year amount (₹ Cr)"},
    ],
    "Portfolio Performance Data": [
        {"field_name": "segment", "field_type": "string", "required": True, "description": "Portfolio segment (e.g., Home Loan, Auto, MSME)"},
        {"field_name": "aum", "field_type": "currency", "required": True, "description": "Assets Under Management (₹ Cr)"},
        {"field_name": "npas", "field_type": "currency", "required": False, "description": "Non-Performing Assets (₹ Cr)"},
        {"field_name": "provision_coverage", "field_type": "number", "required": False, "description": "Provision coverage ratio (%)"},
        {"field_name": "yield_percentage", "field_type": "number", "required": False, "description": "Portfolio yield (%)"},
    ],
}


def get_default_schema(category: str) -> List[Dict[str, Any]]:
    """Get the default extraction schema for a document category."""
    # Try exact match first
    if category in DEFAULT_SCHEMAS:
        return DEFAULT_SCHEMAS[category]

    # Try partial match
    for key in DEFAULT_SCHEMAS:
        if key.lower() in category.lower() or category.lower() in key.lower():
            return DEFAULT_SCHEMAS[key]

    # Default fallback schema
    return [
        {"field_name": "line_item", "field_type": "string", "required": True, "description": "Item name"},
        {"field_name": "value", "field_type": "string", "required": True, "description": "Item value"},
    ]


def get_all_default_schemas() -> Dict[str, List[Dict[str, Any]]]:
    """Return all default schemas."""
    return DEFAULT_SCHEMAS
