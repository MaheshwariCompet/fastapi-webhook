import asyncio
import logging
from fastapi import FastAPI, BackgroundTasks, Header, HTTPException, status, Security
from fastapi.responses import JSONResponse
# Ensure schemas.py is inside an 'app' directory for this import style
from app.schemas import WebhookPayload 

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HookShield — High-Throughput Webhook Ingestion Buffer",
    description="A production-ready asynchronous middleware to ingest and queue webhooks instantly.",
    version="1.0.0"
)

WEBHOOK_SECRET = "secure-webhook-token-2026"

async def verify_webhook_signature(x_webhook_secret: str = Header(..., alias="X-Webhook-Secret")):
    if x_webhook_secret != WEBHOOK_SECRET:
        logger.warning("Unauthorized access attempt rejected.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Webhook-Secret header."
        )
    return x_webhook_secret

async def heavy_webhook_worker(payload: WebhookPayload):
    logger.info(f"Background task started for Event ID: {payload.id}")
    try:
        await asyncio.sleep(4)
        with open("webhook_log.txt", "a") as log_file:
            log_file.write(
                f"[{payload.created_at}] SUCCESS: Processed {payload.event_type} "
                f"for {payload.customer_email} (${payload.amount_cents / 100:.2f})\n"
            )
        logger.info(f"Background processing successfully completed for Event ID: {payload.id}")
    except Exception as e:
        logger.error(f"Failed to process Event ID {payload.id}: {str(e)}")

@app.post(
    "/webhooks/stripe", 
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Security(verify_webhook_signature)],
    summary="Ingest high-volume webhooks",
    response_description="Returns 202 Accepted when queued successfully"
)
async def ingest_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(heavy_webhook_worker, payload)
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "status": "accepted",
            "message": "Webhook received safely and queued for processing.",
            "event_id": str(payload.id)
        }
    )

@app.get("/webhooks/health", status_code=status.HTTP_200_OK, summary="Health Monitor Check")
async def health_check():
    return {"status": "healthy", "service": "HookShield Buffer"}
