# Running on Google Cloud Run

This project is set up to run as a Google Cloud Run service (or Cloud Function gen 2).

## Prerequisites

1.  A Google Cloud Project.
2.  A Service Account with Domain-Wide Delegation enabled and necessary scopes.
3.  The Service Account JSON key file.

## Local Development

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Run the function locally using `functions-framework`:
    ```bash
    export SERVICE_ACCOUNT_FILE="/path/to/your/service-account.json"
    export ADMIN_EMAIL="your-admin@envsn.com"
    functions-framework --target=run_scraper --debug
    ```

3.  Test the function:
    ```bash
    curl localhost:8080
    ```

## Deployment to Cloud Run

1.  Build the container image:
    ```bash
    gcloud builds submit --tag gcr.io/PROJECT_ID/gmail-scraper
    ```

2.  Deploy to Cloud Run:
    ```bash
    gcloud run deploy gmail-scraper \
      --image gcr.io/PROJECT_ID/gmail-scraper \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars ADMIN_EMAIL="your-admin@envsn.com" \
      --set-secrets SERVICE_ACCOUNT_FILE=my-secret-name:latest
    ```
    *Note: For security, it is recommended to store the Service Account JSON in Google Secret Manager and mount it or pass it as an environment variable.*

    Alternatively, if you are just testing, you can set the env var to a path inside the container if you COPY the file (not recommended for production secrets).

## Configuration

-   `SERVICE_ACCOUNT_FILE`: Path to the service account JSON key file.
-   `ADMIN_EMAIL`: The admin email to impersonate.
