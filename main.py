import os
import httpx
from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security import APIKeyQuery, APIKeyHeader
from fastapi.responses import JSONResponse

app = FastAPI(title="Unified Multi-Search API Suite")

# Credits Configuration
DEVELOPER_ID = "@wwnlf"
CHANNEL_NAME = "@ix_mrdeath"
CHANNEL_LINK = "https://t.me/ix_mrdeath"
CREDIT_SUPPORT = "@madara_x_support"

# API Key Protection
API_KEY = os.getenv("API_KEY", "baddie")
API_KEY_NAME = "api_key"

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Source APIs Configuration
MOBILE_SOURCE_URL = "https://ankan-dey-number-search-api.hf.space/search"
MOBILE_SOURCE_KEY = "Only"

RC_SOURCE_URL = "https://madara-alapi.onrender.com/search"
RC_SOURCE_KEY = "madara"

TG_SOURCE_URL = "https://madara-alapi.onrender.com/search"
TG_SOURCE_KEY = "madara"


def verify_api_key(
    api_key_q: str = Security(api_key_query),
    api_key_h: str = Security(api_key_header)
):
    if api_key_q == API_KEY or api_key_h == API_KEY:
        return True
    raise HTTPException(
        status_code=401,
        detail={
            "status": "error",
            "message": "Invalid or missing API key.",
            "developer": DEVELOPER_ID,
            "credit": CREDIT_SUPPORT
        }
    )


# Root Endpoint: Displaying all available endpoints without exposing keys
@app.get("/")
def home():
    return {
        "status": "running",
        "system_credits": {
            "developer": DEVELOPER_ID,
            "credit": CREDIT_SUPPORT,
            "channel_link": CHANNEL_LINK
        },
        "available_services": [
            {
                "service": "Mobile Lookup",
                "endpoint": "/search/mobile",
                "method": "GET",
                "params": ["mobile", "api_key"],
                "example": "/search/mobile?mobile=9876543210&api_key=YOUR_API_KEY"
            },
            {
                "service": "Vehicle RC Lookup",
                "endpoint": "/search/vehicle",
                "method": "GET",
                "params": ["vnum", "api_key"],
                "example": "/search/vehicle?vnum=JH10BT9987&api_key=YOUR_API_KEY"
            },
            {
                "service": "Telegram ID Lookup",
                "endpoint": "/search/telegram",
                "method": "GET",
                "params": ["tgnum", "api_key"],
                "example": "/search/telegram?tgnum=6344914555&api_key=YOUR_API_KEY"
            }
        ]
    }


# 1. Mobile Search Endpoint
@app.get("/search/mobile")
async def search_mobile(
    mobile: str = Query(..., description="Target Mobile Number"),
    authenticated: bool = Security(verify_api_key)
):
    clean_mobile = str(mobile).strip()
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                MOBILE_SOURCE_URL,
                params={"api_key": MOBILE_SOURCE_KEY, "mobile": clean_mobile}
            )

        if response.status_code == 200:
            res_json = response.json()
            source_data = res_json.get("data") or res_json.get("result")

            if source_data:
                records = source_data if isinstance(source_data, list) else [source_data]
                formatted_data = []

                for rec in records:
                    formatted_data.append({
                        "mobile": rec.get("mobile", clean_mobile),
                        "name": rec.get("name", "N/A"),
                        "father_name": rec.get("fname", "N/A"),
                        "id": "[Redacted for Privacy]",
                        "address": rec.get("address", "N/A"),
                        "circle": rec.get("circle", "N/A"),
                        "email": rec.get("email", "N/A"),
                        "alt_mobile": rec.get("alt", "N/A")
                    })

                return {
                    "status": "success",
                    "system_credits": {
                        "developer": DEVELOPER_ID,
                        "credit": CREDIT_SUPPORT,
                        "channel_link": CHANNEL_LINK
                    },
                    "data": formatted_data
                }

        return JSONResponse(
            status_code=404,
            content={
                "status": "not_found",
                "message": "Mobile number records not found.",
                "developer": DEVELOPER_ID
            }
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Source server unavailable or timed out.",
                "developer": DEVELOPER_ID
            }
        )


# 2. Vehicle RC Search Endpoint
@app.get("/search/vehicle")
async def search_vehicle(
    vnum: str = Query(..., description="Vehicle registration number"),
    authenticated: bool = Security(verify_api_key)
):
    clean_vnum = str(vnum).strip().upper().replace(" ", "")
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.get(
                RC_SOURCE_URL,
                params={"api_key": RC_SOURCE_KEY, "vnum": clean_vnum}
            )

        if response.status_code == 200:
            res_json = response.json()
            if not res_json.get("status"):
                return JSONResponse(
                    status_code=404,
                    content={
                        "status": "not_found",
                        "message": "Vehicle details not found.",
                        "developer": DEVELOPER_ID
                    }
                )

            return {
                "status": "success",
                "system_credits": {
                    "developer": DEVELOPER_ID,
                    "credit": CREDIT_SUPPORT,
                    "channel_link": CHANNEL_LINK
                },
                "registration_number": res_json.get("registration_number", clean_vnum),
                "owner_information": res_json.get("owner_information", {}),
                "vehicle_information": res_json.get("vehicle_information", {}),
                "technical_specifications": res_json.get("technical_specifications", {}),
                "registration_details": res_json.get("registration_details", {}),
                "insurance_details": res_json.get("insurance_details", {}),
                "pollution_certificate": res_json.get("pollution_certificate", {}),
                "finance_details": res_json.get("finance_details", {}),
                "address": res_json.get("address", {}),
                "other_information": res_json.get("other_information", {})
            }

        return JSONResponse(
            status_code=response.status_code,
            content={
                "status": "not_found",
                "message": "Vehicle record not found.",
                "developer": DEVELOPER_ID
            }
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Source server unavailable or timed out.",
                "developer": DEVELOPER_ID
            }
        )


# 3. Telegram ID Search Endpoint
@app.get("/search/telegram")
async def search_telegram(
    tgnum: str = Query(..., description="Target Telegram numeric ID"),
    authenticated: bool = Security(verify_api_key)
):
    clean_tgnum = str(tgnum).strip()
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.get(
                TG_SOURCE_URL,
                params={"api_key": TG_SOURCE_KEY, "tgnum": clean_tgnum}
            )

        if response.status_code == 200:
            res_json = response.json()
            if not res_json.get("status"):
                return JSONResponse(
                    status_code=404,
                    content={
                        "status": "not_found",
                        "message": "Telegram ID record not found.",
                        "developer": DEVELOPER_ID
                    }
                )

            raw_verification = res_json.get("verification") or "N/A"
            clean_verification = raw_verification.replace("✅", "").strip()

            return {
                "status": "success",
                "system_credits": {
                    "developer": DEVELOPER_ID,
                    "credit": CREDIT_SUPPORT,
                    "channel_link": CHANNEL_LINK
                },
                "telegram_id": res_json.get("telegram_id", clean_tgnum),
                "phone_number": res_json.get("phone_number", "N/A"),
                "country": res_json.get("country", "N/A"),
                "verification": clean_verification,
                "generated": res_json.get("generated")
            }

        return JSONResponse(
            status_code=response.status_code,
            content={
                "status": "not_found",
                "message": "Telegram record not found.",
                "developer": DEVELOPER_ID
            }
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Source server unavailable or timed out.",
                "developer": DEVELOPER_ID
            }
        )
