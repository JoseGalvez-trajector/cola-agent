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
def check_dependent_status_change(previous_amount: float, current_amount: float) -> str:
    """
    Args:
        previous_amount: The previous monthly dollar amount to search for
        current_amount: The current monthly dollar amount to search for
    
    Returns:
        Information about whether the rate change is due to dependent status changes (family member additions/removals) rather than rating increases
    """
    try:
        previous_matches = _search_va_rates(previous_amount)
        current_matches = _search_va_rates(current_amount)
        
        result = f"Dependent Status Change Analysis:\n"
        result += f"Previous Amount: ${previous_amount:,.2f}\n"
        result += f"Current Amount: ${current_amount:,.2f}\n"
        result += f"Change: ${current_amount - previous_amount:+,.2f}\n\n"
        
        result += _format_amount_results("Previous", previous_amount, previous_matches)
        result += "\n"
        result += _format_amount_results("Current", current_amount, current_matches)
        
        if previous_matches and current_matches:
            # Check if there's a matching disability rating and year but different dependent status
            dependent_status_changes = []
            for prev_match in previous_matches:
                for curr_match in current_matches:
                    if (prev_match['rating'] == curr_match['rating'] and 
                        prev_match['year'] == curr_match['year'] and
                        prev_match['dependent_status'] != curr_match['dependent_status']):
                        dependent_status_changes.append({
                            'rating': prev_match['rating'],
                            'year': prev_match['year'],
                            'prev_status': prev_match['dependent_status'],
                            'curr_status': curr_match['dependent_status']
                        })
            
            if dependent_status_changes:
                result += f"\nDEPENDENT STATUS CHANGE IDENTIFIED:\n"
                for change in dependent_status_changes:
                    result += f"   Rating: {change['rating']} in {change['year']}\n"
                    result += f"   Status changed from: {change['prev_status']}\n"
                    result += f"   Status changed to: {change['curr_status']}\n"
                
                if current_amount > previous_amount:
                    result += f"   This is a rate INCREASE of ${current_amount - previous_amount:+,.2f} due to additional family member(s).\n"
                elif current_amount < previous_amount:
                    result += f"   This is a rate DECREASE of ${current_amount - previous_amount:+,.2f} due to family member removal(s).\n"
                else:
                    result += f"   No change in rate amount despite status change.\n"
                    
                result += f"   This is NOT a disability rating increase - it's a dependent status adjustment."
            else:
                # Check if same dependent status but different rating (actual rating change)
                rating_changes = []
                for prev_match in previous_matches:
                    for curr_match in current_matches:
                        if (prev_match['dependent_status'] == curr_match['dependent_status'] and 
                            prev_match['year'] == curr_match['year'] and
                            prev_match['rating'] != curr_match['rating']):
                            rating_changes.append({
                                'dependent_status': prev_match['dependent_status'],
                                'year': prev_match['year'],
                                'prev_rating': prev_match['rating'],
                                'curr_rating': curr_match['rating']
                            })
                
                if rating_changes:
                    result += f"\nThis appears to be a DISABILITY RATING CHANGE, not a dependent status change:\n"
                    for change in rating_changes:
                        result += f"   Status: {change['dependent_status']} in {change['year']}\n"
                        result += f"   Rating changed from {change['prev_rating']} to {change['curr_rating']}\n"
                else:
                    result += f"\nBoth amounts exist but no clear dependent status or rating change pattern identified."
        elif previous_matches or current_matches:
            result += f"\nOnly one amount exists in VA rates - Cannot determine dependent status change."
        else:
            result += f"\nNeither amount found in VA rates - Cannot analyze dependent status change."
        
        return result
        
    except Exception as e:
        return f"Error checking dependent status changes: {str(e)}"


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
            # Check if there's a matching disability rating and dependent status between years
            cola_matches = []
            for prev_match in previous_matches:
                for curr_match in current_matches:
                    if (prev_match['rating'] == curr_match['rating'] and 
                        prev_match['dependent_status'] == curr_match['dependent_status'] and
                        prev_match['year'] != curr_match['year']):
                        cola_matches.append({
                            'rating': prev_match['rating'],
                            'dependent_status': prev_match['dependent_status'],
                            'prev_year': prev_match['year'],
                            'curr_year': curr_match['year']
                        })
            
            if cola_matches:
                result += f"\nCOLA (Cost of Living Adjustment) IDENTIFIED:\n"
                for match in cola_matches:
                    result += f"   Rating: {match['rating']}, Status: {match['dependent_status']}\n"
                    result += f"   Changed from {match['prev_year']} (${previous_amount:,.2f}) to {match['curr_year']} (${current_amount:,.2f})\n"
                
                if current_amount > previous_amount:
                    result += f"   This is a COLA increase of ${current_amount - previous_amount:+,.2f}."
                elif current_amount < previous_amount:
                    result += f"   This is a COLA decrease of ${current_amount - previous_amount:+,.2f}."
                else:
                    result += f"   No change in rate amount."
            else:
                result += f"\nBoth amounts exist in VA rates but NOT a COLA - different ratings/statuses or same year."
        elif previous_matches or current_matches:
            result += f"\nOnly one amount exists in VA rates - This is NOT a COLA adjustment."
        
        return result
        
    except Exception as e:
        return f"Error checking VA rate changes: {str(e)}"
