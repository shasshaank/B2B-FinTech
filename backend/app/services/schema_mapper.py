"""Schema mapping service for document extraction schemas."""
from typing import Dict, Any, List

# Default extraction schemas per document category
DEFAULT_SCHEMAS = {
    "ALM (Asset-Liability Management)": [
        {"field_name": "maturity_bucket", "field_type": "string", "required": True, "description": "Time bucket (e.g., 0-30 days, 31-90 days)"},
        {"field_name": "assets_amount", "field_type": "currency", "required": True, "description": "Total assets in the bucket (in Cr)"},
        {"field_name": "liabilities_amount", "field_type": "currency", "required": True, "description": "Total liabilities in the bucket (in Cr)"},
        {"field_name": "gap", "field_type": "currency", "required": True, "description": "Gap = Assets - Liabilities (in Cr)"},
        {"field_name": "cumulative_gap", "field_type": "currency", "required": False, "description": "Running cumulative gap (in Cr)"},
    ],
    "Shareholding Pattern": [
        {"field_name": "shareholder_name", "field_type": "string", "required": True, "description": "Name of the shareholder"},
        {"field_name": "holding_percentage", "field_type": "number", "required": True, "description": "Percentage of shares held"},
        {"field_name": "share_count", "field_type": "number", "required": False, "description": "Number of shares held"},
        {"field_name": "shareholder_category", "field_type": "string", "required": False, "description": "Category (Promoter/FII/DII/Public)"},
    ],
    "Borrowing Profile": [
        {"field_name": "lender_name", "field_type": "string", "required": True, "description": "Name of the lending institution"},
        {"field_name": "facility_type", "field_type": "string", "required": True, "description": "Type of credit facility"},
        {"field_name": "sanctioned_amount", "field_type": "currency", "required": True, "description": "Total sanctioned amount (in Cr)"},
        {"field_name": "outstanding_amount", "field_type": "currency", "required": True, "description": "Current outstanding amount (in Cr)"},
        {"field_name": "interest_rate", "field_type": "number", "required": False, "description": "Interest rate (%)"},
        {"field_name": "maturity_date", "field_type": "date", "required": False, "description": "Maturity/repayment date"},
    ],
    "Annual Report - Profit & Loss": [
        {"field_name": "line_item", "field_type": "string", "required": True, "description": "P&L line item name"},
        {"field_name": "fy_current", "field_type": "currency", "required": True, "description": "Current financial year value (in Cr)"},
        {"field_name": "fy_previous", "field_type": "currency", "required": False, "description": "Previous financial year value (in Cr)"},
        {"field_name": "fy_two_years_ago", "field_type": "currency", "required": False, "description": "Value from two years ago (in Cr)"},
    ],
    "Annual Report - Balance Sheet": [
        {"field_name": "line_item", "field_type": "string", "required": True, "description": "Balance sheet line item name"},
        {"field_name": "fy_current", "field_type": "currency", "required": True, "description": "Current financial year value (in Cr)"},
        {"field_name": "fy_previous", "field_type": "currency", "required": False, "description": "Previous financial year value (in Cr)"},
        {"field_name": "fy_two_years_ago", "field_type": "currency", "required": False, "description": "Value from two years ago (in Cr)"},
    ],
    "Annual Report - Cash Flow": [
        {"field_name": "line_item", "field_type": "string", "required": True, "description": "Cash flow line item name"},
        {"field_name": "fy_current", "field_type": "currency", "required": True, "description": "Current financial year value (in Cr)"},
        {"field_name": "fy_previous", "field_type": "currency", "required": False, "description": "Previous financial year value (in Cr)"},
        {"field_name": "fy_two_years_ago", "field_type": "currency", "required": False, "description": "Value from two years ago (in Cr)"},
    ],
    "Portfolio Performance Data": [
        {"field_name": "segment", "field_type": "string", "required": True, "description": "Portfolio segment name"},
        {"field_name": "aum", "field_type": "currency", "required": True, "description": "Assets Under Management (in Cr)"},
        {"field_name": "npas", "field_type": "currency", "required": False, "description": "Non-Performing Assets (in Cr)"},
        {"field_name": "provision_coverage", "field_type": "number", "required": False, "description": "Provision coverage ratio (%)"},
        {"field_name": "yield_percentage", "field_type": "number", "required": False, "description": "Portfolio yield (%)"},
    ],
}


def get_default_schema(category: str) -> List[Dict[str, Any]]:
    """Get the default extraction schema for a document category."""
    return DEFAULT_SCHEMAS.get(category, DEFAULT_SCHEMAS["Annual Report - Balance Sheet"])


def get_all_default_schemas() -> Dict[str, Any]:
    """Get all default extraction schemas."""
    return DEFAULT_SCHEMAS


def merge_schemas(default_schema: List[Dict], custom_schema: List[Dict]) -> List[Dict]:
    """Merge custom schema fields with default schema."""
    if not custom_schema:
        return default_schema
    return custom_schema
