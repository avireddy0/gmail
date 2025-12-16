# Gmail Scraper - Cloud Run Deployment

This project scrapes Gmail messages from your Google Workspace domain and stores them in BigQuery.

## Architecture

- **Cloud Run**: Hosts the Gmail scraper service
- **BigQuery**: Stores scraped email data (`claude-mcp-457317.gmail_analytics.messages`)
- **Gmail API**: Accesses email data via domain-wide delegation
- **Admin Directory API**: Lists all users in the domain

## Prerequisites

1. A Google Cloud Project (`claude-mcp-457317`)
2. A Service Account with Domain-Wide Delegation enabled
3. The Service Account JSON key file
4. BigQuery dataset `gmail_analytics` created in your project

### Required Service Account Permissions

- `roles/bigquery.dataEditor` - To write to BigQuery
- `roles/bigquery.jobUser` - To run BigQuery jobs
- Domain-wide delegation scopes:
  - `https://www.googleapis.com/auth/gmail.readonly`
  - `https://www.googleapis.com/auth/admin.directory.user.readonly`

## Quick Deployment

### Option 1: Using deploy.sh script

```bash
# 1. Ensure you have the service account key at:
#    ~/claude-mcp-457317-069a2a199017.json

# 2. Authenticate gcloud
gcloud auth login

# 3. Run deployment
./deploy.sh
```

### Option 2: Using Cloud Build (Recommended)

```bash
# 1. Authenticate
gcloud auth login
gcloud config set project claude-mcp-457317

# 2. Copy service account key to project directory
cp ~/claude-mcp-457317-069a2a199017.json ./service-account-key.json

# 3. Submit build
gcloud builds submit --config=cloudbuild.yaml
```

### Option 3: Manual Deployment

```bash
# 1. Authenticate
gcloud auth login
gcloud config set project claude-mcp-457317

# 2. Copy service account key
cp ~/claude-mcp-457317-069a2a199017.json ./service-account-key.json

# 3. Deploy to Cloud Run
gcloud run deploy gmail-scraper \
  --source . \
  --project=claude-mcp-457317 \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --service-account=claude-service-account@claude-mcp-457317.iam.gserviceaccount.com \
  --set-env-vars="PROJECT_ID=claude-mcp-457317,DATASET_ID=gmail_analytics,TABLE_ID=messages,ADMIN_EMAIL=avi@envsn.com" \
  --timeout=3600 \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=1
```

## Usage

### Health Check (GET)

```bash
curl https://YOUR-SERVICE-URL/
```

Response:
```json
{
  "status": "healthy",
  "service": "gmail-scraper",
  "project": "claude-mcp-457317",
  "dataset": "gmail_analytics",
  "table": "messages"
}
```

### Trigger Scrape (POST)

```bash
curl -X POST https://YOUR-SERVICE-URL/ \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "after:2024/12/01",
    "max_per_user": 100
  }'
```

Parameters:
- `query`: Gmail search query (e.g., `after:2024/12/01`, `subject:RFI`)
- `max_per_user`: Maximum emails to scrape per user (default: 100)

Response:
```json
{
  "status": "completed",
  "users_processed": 10,
  "total_emails": 500,
  "total_users": 10,
  "errors": []
}
```

## BigQuery Schema

The `messages` table has the following schema:

| Field | Type | Description |
|-------|------|-------------|
| message_id | STRING | Gmail message ID |
| thread_id | STRING | Gmail thread ID |
| user_email | STRING | Email address of the mailbox owner |
| from_address | STRING | Sender email address |
| to_address | STRING | Recipient email addresses |
| cc_address | STRING | CC recipients |
| bcc_address | STRING | BCC recipients |
| subject | STRING | Email subject |
| body_snippet | STRING | Short preview of body (500 chars) |
| body_text | STRING | Full plain text body |
| date_sent | TIMESTAMP | When the email was sent |
| label_ids | STRING (REPEATED) | Gmail labels |
| is_unread | BOOLEAN | Whether email is unread |
| has_attachments | BOOLEAN | Whether email has attachments |
| attachment_count | INTEGER | Number of attachments |
| size_estimate | INTEGER | Estimated size in bytes |
| scraped_at | TIMESTAMP | When the email was scraped |

## Query Examples

```sql
-- Count emails by user
SELECT user_email, COUNT(*) as email_count
FROM `claude-mcp-457317.gmail_analytics.messages`
GROUP BY user_email
ORDER BY email_count DESC;

-- Recent emails with attachments
SELECT user_email, from_address, subject, date_sent
FROM `claude-mcp-457317.gmail_analytics.messages`
WHERE has_attachments = TRUE
  AND date_sent > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
ORDER BY date_sent DESC;

-- Unread emails by user
SELECT user_email, COUNT(*) as unread_count
FROM `claude-mcp-457317.gmail_analytics.messages`
WHERE is_unread = TRUE
GROUP BY user_email;
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SERVICE_ACCOUNT_FILE="/path/to/service-account-key.json"
export ADMIN_EMAIL="avi@envsn.com"
export PROJECT_ID="claude-mcp-457317"
export DATASET_ID="gmail_analytics"
export TABLE_ID="messages"

# Run locally
functions-framework --target=run_scraper --debug

# Test
curl -X POST localhost:8080 \
  -H 'Content-Type: application/json' \
  -d '{"query": "after:2024/12/01", "max_per_user": 10}'
```

## Troubleshooting

1. **Authentication errors**: Ensure domain-wide delegation is configured correctly
2. **BigQuery errors**: Verify the service account has BigQuery permissions
3. **Timeout errors**: Increase `--timeout` or reduce `max_per_user`
