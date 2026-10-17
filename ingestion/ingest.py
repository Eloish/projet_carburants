"""Récupère le flux instantané des prix des carburants et le dépose brut sur S3.

Un snapshot par exécution, rangé sous <YYYY-MM-DD_HH-MM>/prix_bruts.json (heure UTC).
Le script échoue (code de sortie non nul) si quoi que ce soit se passe mal,
pour que GitHub Actions affiche le job en rouge au lieu de passer inaperçu.
"""

import logging
import os
from datetime import datetime, timezone

import boto3
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

BUCKET_NAME = os.getenv("BUCKET_NAME")
API_URL = (
    "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "prix-des-carburants-en-france-flux-instantane-v2/exports/json"
)
REQUEST_TIMEOUT = 120  # secondes : l'export complet pèse plusieurs dizaines de Mo
SNAPSHOT_FILE = "prix_bruts.json"


def build_session() -> requests.Session:
    """Session HTTP avec 3 nouvelles tentatives (délai croissant) sur les erreurs temporaires."""
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=2,  # attentes de 2 s, 4 s, 8 s
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def fetch_carburants() -> tuple[bytes, int]:
    """Télécharge le flux. Retourne les octets bruts reçus et le nombre de stations."""
    log.info("Téléchargement du flux carburants...")
    response = build_session().get(API_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()  # lève une exception si le code HTTP n'est pas 2xx

    data = response.json()
    if not isinstance(data, list) or not data:
        raise ValueError("Réponse inattendue de l'API : liste de stations vide ou absente.")

    log.info("%d stations récupérées", len(data))
    return response.content, len(data)


def upload_to_s3(body: bytes) -> str:
    """Envoie le snapshot brut sur S3 et retourne sa clé."""
    if not BUCKET_NAME:
        raise ValueError("BUCKET_NAME n'est pas défini (.env ou variable d'environnement).")

    # Ex : 2026-10-18_07-00/prix_bruts.json (UTC, identique sur ton PC et sur GitHub)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
    key = f"{stamp}/{SNAPSHOT_FILE}"

    log.info("Envoi sur S3 : s3://%s/%s (%.1f Mo)", BUCKET_NAME, key, len(body) / 1_000_000)
    boto3.client("s3").put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=body,
        ContentType="application/json",
    )
    log.info("Snapshot sauvegardé.")
    return key


def main() -> None:
    body, _ = fetch_carburants()
    upload_to_s3(body)


if __name__ == "__main__":
    main()