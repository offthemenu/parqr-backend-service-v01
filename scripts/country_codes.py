"""
Servicing Countries Mapping for parQR

This mapping provides countries that parQR services with their ISO codes and dialing codes.
Format: {"Country Name": {"country_iso": "XX", "country_code": "+XXX"}}

Usage:
    from scripts.country_codes import SERVICING_COUNTRIES
    
    korea_info = SERVICING_COUNTRIES["South Korea"]  # Returns {"country_iso": "KR", "country_code": "+82"}
    country_list = list(SERVICING_COUNTRIES.keys())  # For dropdown options
"""

SERVICING_COUNTRIES = {
    "South Korea": {"country_iso": "KR", "country_code": "+82"}
}

ALL_COUNTRIES = {
    # Asia-Pacific
    "South Korea": {"country_iso": "KR", "country_code": "+82"},
    "Japan": {"country_iso": "JP", "country_code": "+81"},
    "China": {"country_iso": "CN", "country_code": "+86"},
    "Taiwan": {"country_iso": "TW", "country_code": "+886"},
    "Hong Kong": {"country_iso": "HK", "country_code": "+852"},
    "Singapore": {"country_iso": "SG", "country_code": "+65"},
    "Malaysia": {"country_iso": "MY", "country_code": "+60"},
    "Thailand": {"country_iso": "TH", "country_code": "+66"},
    "Vietnam": {"country_iso": "VN", "country_code": "+84"},
    "Philippines": {"country_iso": "PH", "country_code": "+63"},
    "Indonesia": {"country_iso": "ID", "country_code": "+62"},
    "India": {"country_iso": "IN", "country_code": "+91"},
    "Australia": {"country_iso": "AU", "country_code": "+61"},
    "New Zealand": {"country_iso": "NZ", "country_code": "+64"},
    
    # North America
    "United States": {"country_iso": "US", "country_code": "+1"},
    "Canada": {"country_iso": "CA", "country_code": "+1"},
    "Mexico": {"country_iso": "MX", "country_code": "+52"},
    
    # Europe
    "United Kingdom": {"country_iso": "GB", "country_code": "+44"},
    "Germany": {"country_iso": "DE", "country_code": "+49"},
    "France": {"country_iso": "FR", "country_code": "+33"},
    "Italy": {"country_iso": "IT", "country_code": "+39"},
    "Spain": {"country_iso": "ES", "country_code": "+34"},
    "Netherlands": {"country_iso": "NL", "country_code": "+31"},
    "Sweden": {"country_iso": "SE", "country_code": "+46"},
    "Norway": {"country_iso": "NO", "country_code": "+47"},
    "Denmark": {"country_iso": "DK", "country_code": "+45"},
    "Finland": {"country_iso": "FI", "country_code": "+358"},
    "Switzerland": {"country_iso": "CH", "country_code": "+41"},
    "Austria": {"country_iso": "AT", "country_code": "+43"},
    
    # Other Major Markets
    "Brazil": {"country_iso": "BR", "country_code": "+55"},
    "Argentina": {"country_iso": "AR", "country_code": "+54"},
    "Chile": {"country_iso": "CL", "country_code": "+56"},
    "South Africa": {"country_iso": "ZA", "country_code": "+27"},
    "Israel": {"country_iso": "IL", "country_code": "+972"},
    "United Arab Emirates": {"country_iso": "AE", "country_code": "+971"},
}

def get_country_info(country_name: str) -> dict:
    """
    Get country information by country name.
    
    Args:
        country_name: Full country name (e.g., "South Korea", "United States")
        
    Returns:
        Dictionary with country_iso and country_code
        
    Raises:
        KeyError: If country is not found
        
    Example:
        >>> get_country_info("South Korea")
        {"country_iso": "KR", "country_code": "+82"}
    """
    return SERVICING_COUNTRIES[country_name]

def get_country_by_iso(country_iso: str) -> str:
    """
    Get country name by ISO code.
    
    Args:
        country_iso: Two-letter ISO code (e.g., "KR", "US")
        
    Returns:
        Full country name
        
    Raises:
        KeyError: If ISO code is not found
    """
    for country_name, info in SERVICING_COUNTRIES.items():
        if info["country_iso"] == country_iso.upper():
            return country_name
    raise KeyError(f"Country with ISO code '{country_iso}' not found")

def is_valid_country_iso(country_iso: str) -> bool:
    """
    Check if a country ISO code is valid and serviced.
    
    Args:
        country_iso: Two-letter country code to validate
        
    Returns:
        True if country is serviced, False otherwise
    """
    return any(info["country_iso"] == country_iso.upper() for info in SERVICING_COUNTRIES.values())

def get_servicing_countries_list() -> list[str]:
    """
    Get list of all servicing country names for dropdown usage.
    
    Returns:
        List of country names sorted alphabetically
        
    Example:
        >>> get_servicing_countries_list()
        ["Argentina", "Australia", "Austria", "Brazil", ...]
    """
    return sorted(SERVICING_COUNTRIES.keys())