"""Télécharge le dataset Telco Customer Churn (public) dans data/telco_churn.csv."""
from pathlib import Path
import requests

URL = (
    "https://raw.githubusercontent.com/IBM/"
    "telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
)
DEST = Path(__file__).resolve().parents[1] / "data" / "telco_churn.csv"


def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    print(f"Téléchargement depuis {URL} ...")
    resp = requests.get(URL, timeout=30)
    resp.raise_for_status()
    DEST.write_bytes(resp.content)
    print(f"OK -> {DEST} ({DEST.stat().st_size} octets)")


if __name__ == "__main__":
    main()
