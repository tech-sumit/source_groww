# <img width="150" height="50" alt="image" src="https://github.com/user-attachments/assets/ff1b7a30-79a8-426b-b647-5c40ca26798f" /> Groww Trade API - Airbyte Source Connector

A custom Airbyte source connector for the [Groww Trade API](https://groww.in/trade-api/docs), enabling automated data extraction of trading data including holdings, positions, orders, and margin information.

## Docker Image

```
mrsumit/source-groww:latest
```

## Quick Start

### Add to Airbyte

1. Open your Airbyte instance (e.g., `http://localhost:8000`)
2. Navigate to **Settings** → **Sources** → **+ New Connector**
3. Fill in the details:
   - **Connector Display Name**: `Groww Trade API`
   - **Docker Repository Name**: `mrsumit/source-groww`
   - **Docker Image Tag**: `latest` (or specific version like `0.1.0`)
   - **Connector Documentation URL**: `https://groww.in/trade-api/docs`
4. Click **Add**

### Configure Source

When creating a new Groww source connection, you have two authentication options:

#### Option 1: TOTP Authentication (Recommended)

| Field | Description |
|-------|-------------|
| `totp_token` | Your TOTP Token from [Groww API Keys](https://groww.in/trade-api/api-keys) |
| `totp_secret` | Your TOTP Secret from Groww API Keys |
| `segment` | Market segment: `CASH`, `FNO`, or `COMMODITY` |

#### Option 2: Direct Access Token

| Field | Description |
|-------|-------------|
| `access_token` | Pre-generated Groww API access token |
| `segment` | Market segment: `CASH`, `FNO`, or `COMMODITY` |

## Available Streams

| Stream | Description | Primary Key |
|--------|-------------|-------------|
| `user_profile` | User account details and enabled trading segments | `vendor_user_id` |
| `holdings` | DEMAT holdings with quantities and average prices | `isin` |
| `positions` | Open trading positions (segment-specific) | `trading_symbol`, `exchange`, `product` |
| `margin` | Available margin and collateral details | - |
| `orders` | Order history with status and fill details | `groww_order_id` |

## Local Testing

### Test with Docker

```bash
# Pull the image
docker pull mrsumit/source-groww:latest

# Test spec
docker run --rm mrsumit/source-groww:latest spec

# Test check (with config file)
docker run --rm -v /path/to/config.json:/config.json \
  mrsumit/source-groww:latest check --config /config.json

# Test discover
docker run --rm -v /path/to/config.json:/config.json \
  mrsumit/source-groww:latest discover --config /config.json
```

### Sample Config

```json
{
  "totp_token": "YOUR_TOTP_TOKEN",
  "totp_secret": "YOUR_TOTP_SECRET",
  "segment": "CASH"
}
```

## Getting Groww API Credentials

1. Go to [Groww Trade API Keys](https://groww.in/trade-api/api-keys)
2. Click **Generate TOTP token** under the "Generate API Key" dropdown
3. Copy the **TOTP Token** and **TOTP Secret**
4. Use these values in your Airbyte source configuration

## Sync Modes

All streams support **Full Refresh** sync mode.

## Rate Limits

The connector respects Groww API rate limits. Refer to [Groww API Documentation](https://groww.in/trade-api/docs) for current limits.

## Support

- **Groww API Documentation**: https://groww.in/trade-api/docs
- **Airbyte Documentation**: https://docs.airbyte.com

## License

MIT
