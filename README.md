# Riot Database Maker

## Virtual Environment

Activate the local `uv` virtual environment:

```bash
source _uv_active.sh
```

Check the Python version:

```bash
python --version
```

## Riot API Rate Limit

Control the shared delay between Riot API calls in `config.yaml`:

```yaml
riot:
  request_sleep_seconds: 1.2
```

Create one API client from `configs`; core API functions will use the shared delay automatically.

```python
from src.core.riot_api import RiotApiClient

client = RiotApiClient(api_key, configs)
```
