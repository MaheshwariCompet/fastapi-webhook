from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr

class WebhookPayload(BaseModel):
    id: UUID = Field(..., description="Unique event identifier from the payment gateway")
    event_type: str = Field(..., json_schema_extra={"example": "payment.succeeded"}, description="Type of webhook event")
    created_at: datetime = Field(default_factory=datetime.now) # Timezone-safe local default
    amount_cents: int = Field(..., gt=0, description="Transaction amount in cents")
    currency: str = Field(default="USD", min_length=3, max_length=3)
    customer_email: EmailStr = Field(..., description="Customer email address for invoice generation")

    # Fixed configuration layout syntax for modern Pydantic V2
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "event_type": "payment.succeeded",
                    "amount_cents": 4900,
                    "currency": "USD",
                    "customer_email": "developer@example.com"
                }
            ]
        }
    }
