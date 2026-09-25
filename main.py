import os
import httpx
from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security import APIKeyQuery, APIKeyHeader
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Core Intelligence API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# Identity & Branding Setup
BRAND_NAME = "Core Intelligence Suite"
DEVELOPER = "@wwnlf"
CHANNEL = "@ix_mrdeath"
CHANNEL_URL = "https://t.me/ix_mrdeath"
SUPPORT = "@madara_x_support"

AUTH_KEY = os.getenv("API_KEY", "baddie")
AUTH_PARAM_NAME = "api_key"

key_query = APIKeyQuery(name=AUTH_PARAM_NAME, auto_error=False)
key_header = APIKeyHeader(name=AUTH_PARAM_NAME, auto_error=False)

# Internal Gateway Endpoints
_GW_V = "https://madara-alapi.onrender.com/search"
_GW_VK = "madara"

_GW_T = "https://madara-alapi.onrender.com/search"
_GW_TK = "madara"

_GW_M = "https://ankan-dey-number-search-api.hf.space/search"
_GW_MK = "Only"


def authenticate_client(
    param_k: str = Security(key_query),
    header_k: str = Security(key_header)
):
    if param_k == AUTH_KEY or header_k == AUTH_KEY:
        return True
    raise HTTPException(
        status_code=401,
        detail={
            "status": False,
            "error": "Unauthorized",
            "message": "Valid API key is required to access this service.",
            "developer": DEVELOPER,
            "channel": CHANNEL,
            "support": SUPPORT
        }
    )


def sanitize_records(data_list):
    """Ensures sensitive government identification numbers remain redacted."""
    sanitized = []
    sensitive_keys = {"aadhar", "aadhaar", "uid", "uidai", "id"}
    for record in data_list:
        if isinstance(record, dict):
            clean_rec = {}
            for k, v in record.items():
                if k.lower() in sensitive_keys:
                    clean_rec[k] = "[Redacted for Privacy]"
                else:
                    clean_rec[k] = v
            sanitized.append(clean_rec)
        else:
            sanitized.append(record)
    return sanitized


# Home Documentation Route
@app.get("/")
def gateway_index():
    return {
        "status": True,
        "service": BRAND_NAME,
        "developer": DEVELOPER,
        "channel": CHANNEL,
        "community": CHANNEL_URL,
        "support": SUPPORT,
        "endpoints": [
            {
                "path": "/api/v1/vehicle",
                "method": "GET",
                "description": "Vehicle Registration & RC Details",
                "parameters": {
                    "vnum": "Vehicle Registration Number (Required)",
                    "api_key": "Access Key (Required)"
                },
                "example_usage": "/api/v1/vehicle?vnum=JH10BT9987&api_key=[YOUR_KEY]"
            },
            {
                "path": "/api/v1/telegram",
                "method": "GET",
                "description": "Telegram Account Identification",
                "parameters": {
                    "tgnum": "Telegram Numeric User ID (Required)",
                    "api_key": "Access Key (Required)"
                },
                "example_usage": "/api/v1/telegram?tgnum=6344914555&api_key=[YOUR_KEY]"
            },
            {
                "path": "/api/v1/lookup",
                "method": "GET",
                "description": "Mobile Subscriber Query",
                "parameters": {
                    "mobile": "10-Digit Mobile Number (Required)",
                    "api_key": "Access Key (Required)"
                },
                "example_usage": "/api/v1/lookup?mobile=9006030345&api_key=[YOUR_KEY]"
            }
        ]
    }


# 1. Vehicle RC Intelligence Route
@app.get("/api/v1/vehicle")
async def get_vehicle_info(
    vnum: str = Query(..., description="Vehicle registration identifier"),
    authorized: bool = Security(authenticate_client)
):
    target = str(vnum).strip().upper().replace(" ", "")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(_GW_V, params={"api_key": _GW_VK, "vnum": target})

        if resp.status_code == 200:
            raw = resp.json()
            if not raw.get("status"):
                return JSONResponse(
                    status_code=404,
                    content={
                        "status": False,
                        "message": "Record not found.",
                        "developer": DEVELOPER,
                        "channel": CHANNEL
                    }
                )

            return {
                "status": True,
                "developer": DEVELOPER,
                "channel": CHANNEL,
                "community": CHANNEL_URL,
                "support": SUPPORT,
                "registration_number": raw.get("registration_number", target),
                "owner_information": raw.get("owner_information", {}),
                "vehicle_information": raw.get("vehicle_information", {}),
                "technical_specifications": raw.get("technical_specifications", {}),
                "registration_details": raw.get("registration_details", {}),
                "insurance_details": raw.get("insurance_details", {}),
                "pollution_certificate": raw.get("pollution_certificate", {}),
                "finance_details": raw.get("finance_details", {}),
                "address": raw.get("address", {}),
                "other_information": raw.get("other_information", {})
            }

        return JSONResponse(
            status_code=404,
            content={
                "status": False,
                "message": "Vehicle details not available.",
                "developer": DEVELOPER,
                "channel": CHANNEL
            }
        )

    except Exception:
        return JSONResponse(
            status_code=504,
            content={
                "status": False,
                "message": "Processing service timeout. Please try again.",
                "developer": DEVELOPER,
                "channel": CHANNEL
            }
        )


# 2. Telegram OSINT Route
@app.get("/api/v1/telegram")
async def get_telegram_info(
    tgnum: str = Query(..., description="Telegram Numeric Account ID"),
    authorized: bool = Security(authenticate_client)
):
    target = str(tgnum).strip()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(_GW_T, params={"api_key": _GW_TK, "tgnum": target})

        if resp.status_code == 200:
            raw = resp.json()
            if not raw.get("status"):
                return JSONResponse(
                    status_code=404,
                    content={
                        "status": False,
                        "message": "Record not found.",
                        "developer": DEVELOPER,
                        "channel": CHANNEL
                    }
                )

            verification_status = str(raw.get("verification", "ACTIVE")).replace("✅", "").strip()

            return {
                "status": True,
                "developer": DEVELOPER,
                "channel": CHANNEL,
                "community": CHANNEL_URL,
                "support": SUPPORT,
                "telegram_id": raw.get("telegram_id", target),
                "phone_number": raw.get("phone_number", "N/A"),
                "country": raw.get("country", "INDIA"),
                "verification": verification_status,
                "generated": raw.get("generated")
            }

        return JSONResponse(
            status_code=404,
            content={
                "status": False,
                "message": "Telegram ID record not found.",
                "developer": DEVELOPER,
                "channel": CHANNEL
            }
        )

    except Exception:
        return JSONResponse(
            status_code=504,
            content={
                "status": False,
                "message": "Processing service timeout. Please try again.",
                "developer": DEVELOPER,
                "channel": CHANNEL
            }
        )


# 3. Mobile Subscriber Route (Raw Source Schema Retained)
@app.get("/api/v1/lookup")
async def get_mobile_info(
    mobile: str = Query(..., description="Subscriber number"),
    authorized: bool = Security(authenticate_client)
):
    target = str(mobile).strip()

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.get(_GW_M, params={"api_key": _GW_MK, "mobile": target})

        if resp.status_code == 200:
            raw = resp.json()
            extracted = (
                raw.get("data")
                or raw.get("result")
                or raw.get("records")
            )

            if extracted:
                dataset = extracted if isinstance(extracted, list) else [extracted]
                sanitized_data = sanitize_records(dataset)

                return {
                    "status": True,
                    "developer": DEVELOPER,
                    "channel": CHANNEL,
                    "community": CHANNEL_URL,
                    "support": SUPPORT,
                    "query": target,
                    "total_found": len(sanitized_data),
                    "data": sanitized_data
                }

            return JSONResponse(
                status_code=404,
                content={
                    "status": False,
                    "message": "No records found.",
                    "developer": DEVELOPER,
                    "channel": CHANNEL
                }
            )

        return JSONResponse(
            status_code=404,
            content={
                "status": False,
                "message": "Query failed or no data available.",
                "developer": DEVELOPER,
                "channel": CHANNEL
            }
        )

    except Exception:
        return JSONResponse(
            status_code=504,
            content={
                "status": False,
                "message": "Processing service timeout. Please try again.",
                "developer": DEVELOPER,
                "channel": CHANNEL
            }
        )
