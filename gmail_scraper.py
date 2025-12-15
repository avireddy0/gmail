from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import os

# Service account configuration
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE', '/Users/yourpath/claude-mcp-457317-069a2a199017.json')
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/admin.directory.user.readonly'
]

def get_credentials():
    return service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Step 1: Get all users in domain
def get_all_users(admin_email):
    """Get all users in the Google Workspace domain"""
    credentials = get_credentials()
    delegated_creds = credentials.with_subject(admin_email)
    admin_service = build('admin', 'directory_v1', credentials=delegated_creds)
    
    users = []
    page_token = None
    
    while True:
        results = admin_service.users().list(
            customer='my_customer',
            maxResults=500,
            pageToken=page_token
        ).execute()
        
        users.extend(results.get('users', []))
        page_token = results.get('nextPageToken')
        
        if not page_token:
            break
    
    return [user['primaryEmail'] for user in users]

# Step 2: Scrape emails for each user
def scrape_user_emails(user_email, query='', max_results=500):
    """Scrape emails for a specific user"""
    credentials = get_credentials()
    delegated_creds = credentials.with_subject(user_email)
    gmail_service = build('gmail', 'v1', credentials=delegated_creds)
    
    messages = []
    page_token = None
    
    try:
        while True:
            results = gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results,
                pageToken=page_token
            ).execute()
            
            if 'messages' in results:
                for msg in results['messages']:
                    # Get full message details
                    message = gmail_service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    messages.append(message)
            
            page_token = results.get('nextPageToken')
            if not page_token:
                break
                
    except Exception as e:
        print(f"Error scraping {user_email}: {str(e)}")
    
    return messages

# Main execution
def main():
    # Your admin email for initial authentication
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'your-admin@envsn.com')
    
    # Get all users
    print("Fetching all users...")
    all_users = get_all_users(ADMIN_EMAIL)
    print(f"Found {len(all_users)} users")
    
    # Scrape emails for each user
    all_emails = {}
    for user_email in all_users:
        print(f"Scraping emails for {user_email}...")
        
        # Optional: Add query filters
        # query = 'after:2024/01/01'  # Emails after Jan 1, 2024
        # query = 'subject:RFI OR subject:quote'
        query = ''
        
        emails = scrape_user_emails(user_email, query=query, max_results=100)
        all_emails[user_email] = emails
        print(f"  -> Found {len(emails)} emails")
    
    # Save to file
    with open('all_company_emails.json', 'w') as f:
        json.dump(all_emails, f, indent=2)
    
    print(f"\nTotal emails scraped: {sum(len(e) for e in all_emails.values())}")
    return all_emails

if __name__ == '__main__':
    main()
