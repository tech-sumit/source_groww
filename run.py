#!/usr/bin/env python3
"""
Groww Trade API Source Connector for Airbyte.
Supports two authentication modes:
1. Direct access_token
2. TOTP-based authentication (auto-generates access_token)
"""

import sys
import json
import requests
from pathlib import Path
from typing import Any, Mapping, List, Iterable, Optional
from datetime import datetime

from airbyte_cdk.entrypoint import launch
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.models import AirbyteConnectionStatus, Status, SyncMode


class GrowwStream(HttpStream):
    """Base stream for Groww API."""
    
    url_base = "https://api.groww.in/v1/"
    primary_key = None
    
    def __init__(self, access_token: str, **kwargs):
        super().__init__(**kwargs)
        self.access_token = access_token
    
    @property
    def authenticator(self):
        return None  # We handle auth in request_headers
    
    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {
            "Accept": "application/json",
            "X-API-VERSION": "1.0",
            "Authorization": f"Bearer {self.access_token}"
        }
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        if data.get("status") == "SUCCESS":
            payload = data.get("payload", {})
            # If payload is a dict, yield it as single record
            if isinstance(payload, dict):
                yield payload
            # If payload is a list, yield each item
            elif isinstance(payload, list):
                yield from payload


class UserProfile(GrowwStream):
    """User profile stream."""
    primary_key = "vendor_user_id"
    
    def path(self, **kwargs) -> str:
        return "user/detail"


class Holdings(GrowwStream):
    """Holdings stream."""
    primary_key = "isin"
    
    def path(self, **kwargs) -> str:
        return "holdings/user"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        if data.get("status") == "SUCCESS":
            holdings = data.get("payload", {}).get("holdings", [])
            yield from holdings


class Positions(GrowwStream):
    """Positions stream."""
    primary_key = ["trading_symbol", "exchange", "product"]
    
    def __init__(self, access_token: str, segment: str = "CASH", **kwargs):
        super().__init__(access_token=access_token, **kwargs)
        self.segment = segment
    
    def path(self, **kwargs) -> str:
        return "positions/user"
    
    def request_params(self, **kwargs) -> Mapping[str, Any]:
        return {"segment": self.segment}
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        if data.get("status") == "SUCCESS":
            positions = data.get("payload", {}).get("positions", [])
            yield from positions


class Margin(GrowwStream):
    """Margin details stream."""
    
    def path(self, **kwargs) -> str:
        return "margins/detail/user"


class Orders(GrowwStream):
    """Orders stream."""
    primary_key = "groww_order_id"
    
    def __init__(self, access_token: str, segment: str = "CASH", **kwargs):
        super().__init__(access_token=access_token, **kwargs)
        self.segment = segment
    
    def path(self, **kwargs) -> str:
        return "order/list"
    
    def request_params(self, **kwargs) -> Mapping[str, Any]:
        return {"segment": self.segment}
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        if data.get("status") == "SUCCESS":
            orders = data.get("payload", {}).get("order_list", [])
            yield from orders


class SourceGroww(AbstractSource):
    """
    Groww Trade API Source with TOTP authentication support.
    """
    
    def _get_access_token_from_totp(self, totp_token: str, totp_secret: str) -> str:
        """Generate access token using TOTP authentication."""
        import pyotp
        from growwapi import GrowwAPI
        
        totp_gen = pyotp.TOTP(totp_secret)
        totp = totp_gen.now()
        access_token = GrowwAPI.get_access_token(api_key=totp_token, totp=totp)
        return access_token
    
    def _resolve_access_token(self, config: Mapping[str, Any]) -> str:
        """Resolve access token from config or generate from TOTP."""
        if config.get("access_token"):
            return config["access_token"]
        
        totp_token = config.get("totp_token")
        totp_secret = config.get("totp_secret")
        if totp_token and totp_secret:
            return self._get_access_token_from_totp(totp_token, totp_secret)
        
        raise ValueError("Either access_token or (totp_token + totp_secret) must be provided")
    
    def check_connection(self, logger, config: Mapping[str, Any]) -> tuple[bool, Optional[str]]:
        """Check connection to Groww API."""
        try:
            access_token = self._resolve_access_token(config)
            
            # Test API connection
            response = requests.get(
                "https://api.groww.in/v1/user/detail",
                headers={
                    "Accept": "application/json",
                    "X-API-VERSION": "1.0",
                    "Authorization": f"Bearer {access_token}"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "SUCCESS":
                    return True, None
                return False, f"API returned: {data}"
            return False, f"HTTP {response.status_code}: {response.text}"
            
        except Exception as e:
            return False, str(e)
    
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """Return list of streams."""
        access_token = self._resolve_access_token(config)
        segment = config.get("segment", "CASH")
        
        return [
            UserProfile(access_token=access_token),
            Holdings(access_token=access_token),
            Positions(access_token=access_token, segment=segment),
            Margin(access_token=access_token),
            Orders(access_token=access_token, segment=segment),
        ]


def run():
    source = SourceGroww()
    launch(source, sys.argv[1:])


if __name__ == "__main__":
    run()
