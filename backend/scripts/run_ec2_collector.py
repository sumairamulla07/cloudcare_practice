import json
import sys
from datetime import datetime
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.collector.ec2 import collect_ec2_inventory


def default_serializer(value):
    if isinstance(value, datetime):
        return value.isoformat()

    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def main() -> None:
    output = collect_ec2_inventory()

    print(
        json.dumps(
            output,
            indent=2,
            default=default_serializer,
        )
    )


if __name__ == "__main__":
    main()
