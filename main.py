import functions_framework
import json
import os
from gmail_scraper import main as scraper_main

@functions_framework.http
def run_scraper(request):
    """HTTP Cloud Function to trigger the Gmail scraper."""
    try:
        # You can parse request args here if needed
        # request_json = request.get_json(silent=True)
        
        print("Starting scraper...")
        results = scraper_main()
        
        # Return the results as JSON
        return json.dumps(results, default=str), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        print(f"Error running scraper: {e}")
        return f"Error: {str(e)}", 500
