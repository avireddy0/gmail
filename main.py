import functions_framework
import json
import os
from gmail_scraper import main as scraper_main

@functions_framework.http
def run_scraper(request):
    """HTTP Cloud Function to trigger the Gmail scraper.

    Endpoints:
    - GET /: Health check
    - POST /: Trigger scraper with optional parameters

    POST body (optional):
    {
        "query": "after:2024/12/01",  # Gmail search query
        "max_per_user": 100           # Max emails per user
    }
    """
    # Handle health check
    if request.method == 'GET':
        return json.dumps({
            'status': 'healthy',
            'service': 'gmail-scraper',
            'project': os.getenv('PROJECT_ID', 'claude-mcp-457317'),
            'dataset': os.getenv('DATASET_ID', 'gmail_analytics'),
            'table': os.getenv('TABLE_ID', 'messages')
        }), 200, {'Content-Type': 'application/json'}

    # Handle scrape request
    try:
        # Parse request parameters
        request_json = request.get_json(silent=True) or {}
        query = request_json.get('query', '')
        max_per_user = request_json.get('max_per_user', 100)

        print(f"Starting scraper with query='{query}', max_per_user={max_per_user}")

        # Run the scraper
        results = scraper_main(query=query, max_per_user=max_per_user)

        # Return the results as JSON
        return json.dumps(results, default=str), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        print(f"Error running scraper: {e}")
        import traceback
        traceback.print_exc()
        return json.dumps({
            'status': 'error',
            'error': str(e)
        }), 500, {'Content-Type': 'application/json'}
