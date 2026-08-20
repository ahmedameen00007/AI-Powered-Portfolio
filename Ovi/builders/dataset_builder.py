"""
builders/dataset_builder.py

Main dataset processing pipeline for OVI.

Pipeline:

    Raw Data
        ↓
    Load
        ↓
    Normalize
        ↓
    Validate
        ↓
    Save
        ↓
    Processed Data
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Type

from pydantic import BaseModel

from builders.normalizer import DataNormalizer
from builders.validator import DataValidator


class DatasetBuilder:
    """
    Orchestrates the raw → normalized → validated → processed
    dataset pipeline.
    """

    def __init__(
        self,
        raw_dir: str | Path = "dataset/raw/json",
        processed_dir: str | Path = "dataset/processed",
        normalizer: DataNormalizer | None = None,
        validator: DataValidator | None = None,
    ) -> None:

        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)

        self.normalizer = normalizer or DataNormalizer()
        self.validator = validator or DataValidator()

        self.processed_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ================================================================
    # LOAD
    # ================================================================

    def load_json(
        self,
        file_path: str | Path,
    ) -> dict[str, Any]:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Dataset file not found: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise TypeError(
                f"Root JSON must be an object: {path}"
            )

        return data

    # ================================================================
    # SAVE
    # ================================================================

    def save_json(
        self,
        data: dict[str, Any],
        file_path: str | Path,
    ) -> Path:

        path = Path(file_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

        return path

    # ================================================================
    # PATHS
    # ================================================================

    def get_raw_path(
        self,
        filename: str,
    ) -> Path:

        path = self.raw_dir / filename

        if path.suffix.lower() != ".json":
            path = path.with_suffix(".json")

        return path

    def get_processed_path(
        self,
        filename: str,
    ) -> Path:

        path = self.processed_dir / filename

        if path.suffix.lower() != ".json":
            path = path.with_suffix(".json")

        return path

    # ================================================================
    # SINGLE ENTITY
    # ================================================================

    def build_single(
        self,
        data: dict[str, Any],
        schema: Type[BaseModel],
    ) -> dict[str, Any]:

        return self.validator.validate_to_dict(
            data=data,
            schema=schema,
        )

    # ================================================================
    # COLLECTION
    # ================================================================

    def build_collection(
        self,
        data: dict[str, Any],
        collection_key: str,
        schema: Type[BaseModel],
    ) -> dict[str, Any]:

        if collection_key not in data:
            raise KeyError(
                f"Collection key '{collection_key}' not found."
            )

        records = data[collection_key]

        if not isinstance(records, list):
            raise TypeError(
                f"'{collection_key}' must contain a list."
            )

        validated_records = []

        for index, record in enumerate(records):

            if not isinstance(record, dict):
                raise TypeError(
                    f"Record {index} in '{collection_key}' "
                    f"must be an object."
                )

            validated_record = self.validator.validate_to_dict(
                data=record,
                schema=schema,
            )

            validated_records.append(
                validated_record
            )

        return {
            collection_key: validated_records
        }

    # ================================================================
    # BUILD
    # ================================================================

    def build(
        self,
        filename: str,
        schema: Type[BaseModel],
        collection_key: str | None = None,
        normalize: bool = True,
    ) -> dict[str, Any]:

        raw_path = self.get_raw_path(filename)

        raw_data = self.load_json(raw_path)

        # ------------------------------------------------------------
        # Normalize
        # ------------------------------------------------------------

        data = raw_data

        if normalize:
            data = self.normalizer.normalize(
                data=data,
                data_type=filename.removesuffix(".json"),
            )

        # ------------------------------------------------------------
        # Validate
        # ------------------------------------------------------------

        if collection_key is not None:

            processed_data = self.build_collection(
                data=data,
                collection_key=collection_key,
                schema=schema,
            )

        else:

            processed_data = self.build_single(
                data=data,
                schema=schema,
            )

        # ------------------------------------------------------------
        # Save
        # ------------------------------------------------------------

        processed_path = self.get_processed_path(
            filename
        )

        self.save_json(
            data=processed_data,
            file_path=processed_path,
        )

        return processed_data