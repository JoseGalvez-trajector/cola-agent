from strands import tool
import pandas as pd
import os


def _format_amount_results(label: str, amount: float, matches: list) -> str:
    """
    Helper function to format amount search results.
    
    Args:
        label: Label for the amount (e.g., "Previous", "Current")
        amount: The dollar amount
        matches: List of matches from _search_va_rates
    
    Returns:
        Formatted string with the results
    """
    if matches:
        result = f"{label} amount (${amount:,.2f}) found in {len(matches)} rate(s):\n"
        for i, match in enumerate(matches, 1):
            result += f"   {i}. {match['year']} - {match['dependent_status']} - {match['rating']}\n"
    else:
        result = f"{label} amount (${amount:,.2f}) NOT found in VA rates\n"
    return result


def _search_va_rates(amount: float) -> list:
    """
    Helper function to search for a specific amount in VA disability rates.
    
    Args:
        amount: The monthly dollar amount to search for
    
    Returns:
        List of matches with year, dependent_status, rating, and amount
    """
    try:
        csv_path = os.path.join("docs", "va_disability_rates.csv")
        df = pd.read_csv(csv_path)
        
        rating_columns = [col for col in df.columns if '%' in col]
        
        matches = []
        for _, row in df.iterrows():
            year = row['Year']
            dependent_status = row['Dependent Status']
            
            for rating_col in rating_columns:
                rate_value = row[rating_col]
                if pd.notna(rate_value): 
                    if abs(rate_value - amount) < 0.01:
                        matches.append({
                            'year': year,
                            'dependent_status': dependent_status,
                            'rating': rating_col,
                            'amount': rate_value
                        })
        
        return matches
        
    except Exception as e:
        raise Exception(f"Error searching for rate: {str(e)}")


@tool
def find_va_rate_info(amount: float) -> str:
    """
    Args:
        amount: The monthly dollar amount to search for (e.g., 3831.30)
    
    Returns:
        The Year, Dependent Status, and Rating that match the specified amount
    """
    try:
        matches = _search_va_rates(amount)
        
        if not matches:
            return f"No VA rates found matching ${amount:,.2f} per month"
        
        result = f"Found {len(matches)} rate(s) matching ${amount:,.2f} per month:\n\n"
        for i, match in enumerate(matches, 1):
            result += f"{i}. Year: {match['year']}\n   Dependent Status: {match['dependent_status']}\n   Rating: {match['rating']}\n   Amount: ${match['amount']:,.2f}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error searching for rate: {str(e)}"


@tool
def check_va_rate_changes(previous_amount: float, current_amount: float) -> str:
    """
    Args:
        previous_amount: The previous monthly dollar amount to search for
        current_amount: The current monthly dollar amount to search for
    
    Returns:
        Information about whether both amounts exist in the VA disability rates and any changes between them
    """
    try:
        previous_matches = _search_va_rates(previous_amount)
        current_matches = _search_va_rates(current_amount)
        
        result = f"VA Rate Change Analysis:\n"
        result += f"Previous Amount: ${previous_amount:,.2f}\n"
        result += f"Current Amount: ${current_amount:,.2f}\n"
        result += f"Change: ${current_amount - previous_amount:+,.2f}\n\n"
        
        result += _format_amount_results("Previous", previous_amount, previous_matches)
        result += "\n"
        result += _format_amount_results("Current", current_amount, current_matches)
        
        if previous_matches and current_matches:
            result += f"\nBoth amounts exist in VA rates - This represents a COLA (Cost of Living Adjustment). "
            if current_amount > previous_amount:
                result += f"The rate increased from ${previous_amount:,.2f} to ${current_amount:,.2f}."
            elif current_amount < previous_amount:
                result += f"The rate decreased from ${previous_amount:,.2f} to ${current_amount:,.2f}."
            else:
                result += f"No change in rate amount."
        elif previous_matches or current_matches:
            result += f"\nOnly one amount exists in VA rates - This may not be a standard COLA adjustment."
        
        return result
        
    except Exception as e:
        return f"Error checking VA rate changes: {str(e)}"
