"""Charge les snapshots S3 (JSON bruts) dans PostgreSQL : table public.carburants_raw.

Un snapshot par jour est conservé dans la table brute (colonne snapshot_date).
Relancer le script pour une même date remplace ce jour-là, sans doublons.

Usage :
    python load.py                  # charge le snapshot le plus récent
    python load.py --all            # charge tous les snapshots présents sur S3
    python load.py --key 2026-10-17_07-00/prix_bruts.json
"""

import argparse
import json
import logging
import os
from datetime import date
from typing import Any

import boto3
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

BUCKET_NAME = os.getenv("BUCKET_NAME")
SCHEMA = "public"
TABLE = "carburants_raw"
SNAPSHOT_FILE = "prix_bruts.json"

NUMERIC_COLUMNS = [
    "latitude",
    "longitude",
    "gazole_prix",
    "sp95_prix",
    "sp98_prix",
    "e10_prix",
    "e85_prix",
    "gplc_prix",
]


# ---------- S3 ----------
def list_snapshot_keys(s3, bucket: str) -> list[str]:
    """Retourne toutes les clés de snapshots, triées de la plus ancienne à la plus récente."""
    keys = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            if obj["Key"].endswith(f"/{SNAPSHOT_FILE}"):
                keys.append(obj["Key"])
    return sorted(keys)


def fetch_from_s3(s3, bucket: str, key: str) -> list[dict[str, Any]]:
    response = s3.get_object(Bucket=bucket, Key=key)
    data = json.loads(response["Body"].read().decode("utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{key} ne contient pas une liste de stations JSON.")
    return data


def snapshot_date_from_key(key: str) -> date:
    """'2026-10-17_07-00/prix_bruts.json' -> date(2026, 10, 17)"""
    return date.fromisoformat(key.split("/")[0][:10])


# ---------- Transformation ----------
def normalize_records(records: list[dict[str, Any]], key: str) -> pd.DataFrame:
    df = pd.DataFrame(records)

    # Dictionnaires et listes -> chaînes JSON (PostgreSQL ne sait pas les stocker tels quels)
    for col in df.columns:
        df[col] = df[col].apply(
            lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else x
        )

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "cp" in df.columns:
        df["cp"] = df["cp"].apply(
            lambda v: str(v).zfill(5) if pd.notna(v) and str(v).strip() != "" else None
        )

    df["snapshot_date"] = snapshot_date_from_key(key)
    df["snapshot_key"] = key
    df["loaded_at"] = pd.Timestamp.now(tz="UTC")
    return df


# ---------- PostgreSQL ----------
def get_engine() -> Engine:
    db_url = os.getenv("DB_URL")
    if db_url:
        return create_engine(db_url)

    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    name = os.getenv("DB_NAME")
    if not all([user, password, name]):
        raise ValueError("Définis DB_URL, ou bien DB_USER, DB_PASSWORD et DB_NAME dans ton .env.")

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}")


def load_snapshot(engine: Engine, df: pd.DataFrame) -> None:
    """Supprime le snapshot du même jour puis insère le nouveau, dans une seule transaction."""
    snap_date = df["snapshot_date"].iloc[0]

    with engine.begin() as conn:
        if inspect(conn).has_table(TABLE, schema=SCHEMA):
            conn.execute(
                text(f"delete from {SCHEMA}.{TABLE} where snapshot_date = :d"),
                {"d": snap_date},
            )
        df.to_sql(
            name=TABLE,
            con=conn,
            schema=SCHEMA,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi",
        )


# ---------- Main ----------
def main() -> None:
    parser = argparse.ArgumentParser(description="Charge les snapshots S3 dans PostgreSQL.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="charger tous les snapshots S3")
    group.add_argument("--key", help="charger un snapshot précis (clé S3)")
    args = parser.parse_args()

    if not BUCKET_NAME:
        raise ValueError("BUCKET_NAME n'est pas défini dans le .env.")

    s3 = boto3.client("s3")
    engine = get_engine()

    if args.key:
        keys = [args.key]
    else:
        all_keys = list_snapshot_keys(s3, BUCKET_NAME)
        if not all_keys:
            raise RuntimeError("Aucun snapshot trouvé sur S3.")
        keys = all_keys if args.all else [all_keys[-1]]

    for key in keys:
        log.info("Chargement de %s", key)
        records = fetch_from_s3(s3, BUCKET_NAME, key)
        df = normalize_records(records, key)
        load_snapshot(engine, df)
        log.info("%d stations chargées (snapshot_date=%s)", len(df), df["snapshot_date"].iloc[0])

    log.info("Terminé : %d snapshot(s) chargé(s).", len(keys))


if __name__ == "__main__":
    main()