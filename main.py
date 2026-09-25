import os
import httpx
from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security import APIKeyQuery, APIKeyHeader
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Advanced Multi-Intelligence API Suite",
    description="Unified API Wrapper for Vehicle RC, Telegram OSINT, and Mobile Intelligence",
    version="3.0.0"
)

# --- Official System Credits & Channels ---
SYSTEM_CREDITS = {
    "developer": "@wwnlf",
    "channel_name": "@ix_mrdeath",
    "channel_link": "https://t.me/ix_mrdeath",
    "support": "@madara_x_support"
}

# --- Security Configuration ---
API_KEY = os.getenv("API_KEY", "baddie")
API_KEY_NAME = "api_key"

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# --- Source Endpoints Configuration ---
RC_SOURCE_URL = "https://madara-alapi.onrender.com/search"
RC_SOURCE_KEY = "madara"

TG_SOURCE_URL = "https://madara-alapi.onrender.com/search"
TG_SOURCE_KEY = "madara"

MOBILE_SOURCE_URL = "https://ankan-dey-number-search-api.hf.space/search"
MOBILE_SOURCE_KEY = "Only"


def verify_api_key(
    api_key_q: str = Security(api_key_query),
    api_key_h: str = Security(api_key_header)
):
    if api_key_q == API_KEY or api_key_h == API_KEY:
        return True
    raise HTTPException(
        status_code=401,
        detail={
            "status": False,
            "error_code": 401,
            "message": "Invalid or missing access API key.",
            **SYSTEM_CREDITS
        }
    )


# --- Root Directory & Documentation ---
@app.get("/")
def home():
    return {
        "status": True,
        "engine": "Live & Operational",
        "branding": SYSTEM_CREDITS,
        "endpoints": [
            {
                "module": "Vehicle RC Lookup",
                "route": "/search/vehicle",
                "method": "GET",
                "required_params": ["vnum", "api_key"],
                "example": "/search/vehicle?vnum=JH10BT9987&api_key=baddie"
            },
            {
                "module": "Telegram ID Lookup",
                "route": "/search/telegram",
                "method": "GET",
                "required_params": ["tgnum", "api_key"],
                "example": "/search/telegram?tgnum=6344914555&api_key=baddie"
            },
            {
                "module": "Mobile Information Lookup",
                "route": "/search/mobile",
                "method": "GET",
                "required_params": ["mobile", "api_key"],
                "example": "/search/mobile?mobile=9876543210&api_key=baddie"
            }
        ]
    }


# 1️⃣ VEHICLE RC INTELLIGENCE ENDPOINT
@app.get("/search/vehicle")
async def search_vehicle(
    vnum: str = Query(..., description="Vehicle Registration Number (e.g. JH10BT9987)"),
    authenticated: bool = Security(verify_api_key)
):
    clean_vnum = str(vnum).strip().upper().replace(" ", "")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
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
                        "status": False,
                        "message": "Vehicle records not found in database.",
                        **SYSTEM_CREDITS
                    }
                )

            # Response structure jaisa source deta hai exact waisa hi with your branding
            return {
                "status": True,
                **SYSTEM_CREDITS,
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
                "status": False,
                "message": f"Source API returned error HTTP {response.status_code}",
                **SYSTEM_CREDITS
            }
        )

    except Exception:
        return JSONResponse(
            status_code=504,
            content={
                "status": False,
                "message": "Upstream source server timed out or is spinning up.",
                **SYSTEM_CREDITS
            }
        )


# 2️⃣ TELEGRAM OSINT LOOKUP ENDPOINT
@app.get("/search/telegram")
async def search_telegram(
    tgnum: str = Query(..., description="Telegram Numeric Account ID"),
    authenticated: bool = Security(verify_api_key)
):
    clean_tgnum = str(tgnum).strip()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
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
                        "status": False,
                        "message": "Telegram account ID not found in archive.",
                        **SYSTEM_CREDITS
                    }
                )

            # Exact matching structure jaisa source deta hai
            return {
                "status": True,
                **SYSTEM_CREDITS,
                "telegram_id": res_json.get("telegram_id", clean_tgnum),
                "phone_number": res_json.get("phone_number", "N/A"),
                "country": res_json.get("country", "INDIA"),
                "verification": res_json.get("verification", "ACTIVE"),
                "generated": res_json.get("generated", None)
            }

        return JSONResponse(
            status_code=response.status_code,
            content={
                "status": False,
                "message": f"Source API returned status code {response.status_code}",
                **SYSTEM_CREDITS
            }
        )

    except Exception:
        return JSONResponse(
            status_code=504,
            content={
                "status": False,
                "message": "Upstream source server timed out or is offline.",
                **SYSTEM_CREDITS
            }
        )


# 3️⃣ MOBILE INTELLIGENCE ENDPOINT
@app.get("/search/mobile")
async def search_mobile(
    mobile: str = Query(..., description="Target 10-digit mobile number"),
    authenticated: bool = Security(verify_api_key)
):
    clean_mobile = str(mobile).strip()

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.get(
                MOBILE_SOURCE_URL,
                params={"api_key": MOBILE_SOURCE_KEY, "mobile": clean_mobile}
            )

        if response.status_code == 200:
            res_json = response.json()
            raw_data = (
                res_json.get("data")
                or res_json.get("result")
                or res_json.get("records")
            )

            if raw_data:
                records = raw_data if isinstance(raw_data, list) else [raw_data]
                parsed_records = []

                for rec in records:
                    parsed_records.append({
                        "mobile": rec.get("mobile", clean_mobile),
                        "name": rec.get("name", "N/A"),
                        "father_name": rec.get("fname") or rec.get("father_name", "N/A"),
                        "address": rec.get("address", "N/A"),
                        "circle": rec.get("circle", "N/A"),
                        "email": rec.get("email", "N/A"),
                        "alt_mobile": rec.get("alt") or rec.get("alt_mobile", "N/A"),
                        "id": "[Redacted for Privacy]"
                    })

                return {
                    "status": True,
                    **SYSTEM_CREDITS,
                    "query": clean_mobile,
                    "total_found": len(parsed_records),
                    "data": parsed_records
                }

            return JSONResponse(
                status_code=404,
                content={
                    "status": False,
                    "message": "No subscriber record found for this mobile number.",
                    **SYSTEM_CREDITS
                }
            )

        return JSONResponse(
            status_code=response.status_code,
            content={
                "status": False,
                "message": f"Source API failed with code {response.status_code}",
                **SYSTEM_CREDITS
            }
        )

    except Exception:
        return JSONResponse(
            status_code=504,
            content={
                "status": False,
                "message": "Mobile search engine source timed out.",
                **SYSTEM_CREDITS
            }
        )
