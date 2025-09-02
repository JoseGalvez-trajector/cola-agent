from strands import tool
import pandas as pd
import os


def _search_va_rates(amount: float) -> list:
    """
    Helper function to search for a specific amount in VA disability rates.
    
    Args:
        amount: The monthly dollar amount to search for
    
    Returns:
        List of matches with year, dependent_status, rating, and amount
    """
    try:
        # Read the CSV file using pandas
        csv_path = os.path.join("docs", "va_disability_rates.csv")
        df = pd.read_csv(csv_path)
        
        # Get all rating columns (columns with %)
        rating_columns = [col for col in df.columns if '%' in col]
        
        # Search for matches
        matches = []
        for _, row in df.iterrows():
            year = row['Year']
            dependent_status = row['Dependent Status']
            
            for rating_col in rating_columns:
                rate_value = row[rating_col]
                if pd.notna(rate_value):  # Check if the value is not NaN
                    # Check if this rate matches our target amount (with small tolerance for floating point)
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
        
        # Format the results
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
        # Search for both amounts using the shared helper
        previous_matches = _search_va_rates(previous_amount)
        current_matches = _search_va_rates(current_amount)
        
        # Build the result
        result = f"VA Rate Change Analysis:\n"
        result += f"Previous Amount: ${previous_amount:,.2f}\n"
        result += f"Current Amount: ${current_amount:,.2f}\n"
        result += f"Change: ${current_amount - previous_amount:+,.2f}\n\n"
        
        # Check if previous amount exists
        if previous_matches:
            result += f"Previous amount (${previous_amount:,.2f}) found in {len(previous_matches)} rate(s):\n"
            for i, match in enumerate(previous_matches, 1):
                result += f"   {i}. {match['year']} - {match['dependent_status']} - {match['rating']}\n"
        else:
            result += f"Previous amount (${previous_amount:,.2f}) NOT found in VA rates\n"
        
        result += "\n"
        
        # Check if current amount exists
        if current_matches:
            result += f"Current amount (${current_amount:,.2f}) found in {len(current_matches)} rate(s):\n"
            for i, match in enumerate(current_matches, 1):
                result += f"   {i}. {match['year']} - {match['dependent_status']} - {match['rating']}\n"
        else:
            result += f"Current amount (${current_amount:,.2f}) NOT found in VA rates\n"
        
        # Additional analysis if both amounts exist
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
