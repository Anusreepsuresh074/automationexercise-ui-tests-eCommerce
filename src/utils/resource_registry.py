import json
import os
from datetime import UTC, datetime

_REGISTRY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports", "created-resources.jsonl"
)


def record_created_resource(resource_type: str, resource_id: str, environment: str) -> None:
    """Appends an audit record of test data created on the site, so any
    account a crashed run failed to clean up can still be found and
    removed later. Never deletes anything itself."""
    os.makedirs(os.path.dirname(_REGISTRY_PATH), exist_ok=True)
    entry = {
        "resource_type": resource_type,
        "resource_id": resource_id,
        "environment": environment,
        "created_at": datetime.now(UTC).isoformat(),
    }
    with open(_REGISTRY_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
