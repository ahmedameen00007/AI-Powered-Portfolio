"""
builders/validator.py

Validation layer for the OVI data pipeline.

Responsibilities:
- Validate normalized data against OVI Pydantic schemas.
- Convert validation errors into readable errors.
- Validate single records or complete datasets.
- Keep validation logic separate from normalization and persistence.

The validator does NOT:
- Normalize data.
- Modify raw data.
- Build relationships.
- Create chunks.
- Generate embeddings.
- Write files.
"""

from __future__ import annotations

from typing import Any, Type

from pydantic import BaseModel, ValidationError


class DataValidationError(Exception):
    """
    Raised when OVI data fails schema validation.
    """

    def __init__(
        self,
        message: str,
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)

        self.errors = errors or []


class DataValidator:
    """
    Validates OVI data using Pydantic schemas.

    The validator acts as a bridge between the normalized
    dataset and the formal schema layer.

    Example:

        validator = DataValidator()

        validated = validator.validate(
            data,
            schema=CertificationDataset,
        )
    """

    # ------------------------------------------------------------------
    # Basic validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate(
        data: Any,
        schema: Type[BaseModel],
    ) -> BaseModel:
        """
        Validate data against a Pydantic schema.

        Args:
            data:
                Normalized data to validate.

            schema:
                Pydantic model class.

        Returns:
            Validated Pydantic model instance.

        Raises:
            DataValidationError:
                If validation fails.
        """

        try:
            return schema.model_validate(data)

        except ValidationError as exc:
            formatted_errors = []

            for error in exc.errors():
                formatted_errors.append(
                    {
                        "location": DataValidator._format_location(
                            error.get("loc", ())
                        ),
                        "message": error.get("msg", ""),
                        "type": error.get("type", ""),
                        "input": error.get("input"),
                    }
                )

            message = (
                f"Data validation failed for "
                f"{schema.__name__}."
            )

            raise DataValidationError(
                message=message,
                errors=formatted_errors,
            ) from exc

    # ------------------------------------------------------------------
    # Error formatting
    # ------------------------------------------------------------------

    @staticmethod
    def _format_location(
        location: tuple[Any, ...],
    ) -> str:
        """
        Convert Pydantic's nested error location into
        a readable path.

        Example:

            ("certifications", 2, "provider")

        becomes:

            certifications[2].provider
        """

        if not location:
            return "<root>"

        result = ""

        for part in location:
            if isinstance(part, int):
                result += f"[{part}]"
            else:
                if result:
                    result += "."

                result += str(part)

        return result

    # ------------------------------------------------------------------
    # Public validation
    # ------------------------------------------------------------------

    def validate(
        self,
        data: Any,
        schema: Type[BaseModel],
    ) -> BaseModel:
        """
        Validate data against the supplied schema.

        This is the main generic validation method.
        """

        return self._validate(
            data=data,
            schema=schema,
        )

    # ------------------------------------------------------------------
    # Validation to dictionary
    # ------------------------------------------------------------------

    def validate_to_dict(
        self,
        data: Any,
        schema: Type[BaseModel],
    ) -> dict[str, Any]:
        """
        Validate data and return the validated model
        as a dictionary.

        This is useful before writing to dataset/processed/.
        """

        model = self.validate(
            data=data,
            schema=schema,
        )

        return model.model_dump(
            mode="json",
        )

    # ------------------------------------------------------------------
    # Validation to JSON-compatible data
    # ------------------------------------------------------------------

    def validate_to_json(
        self,
        data: Any,
        schema: Type[BaseModel],
    ) -> dict[str, Any]:
        """
        Validate data and return JSON-compatible output.

        This method is intentionally separate from file writing.
        """

        model = self.validate(
            data=data,
            schema=schema,
        )

        return model.model_dump(
            mode="json",
        )

    # ------------------------------------------------------------------
    # Multiple records
    # ------------------------------------------------------------------

    def validate_many(
        self,
        records: list[dict[str, Any]],
        schema: Type[BaseModel],
    ) -> list[BaseModel]:
        """
        Validate multiple records against the same schema.

        Useful for datasets such as:

            experiences
            projects
            certifications
            achievements
        """

        validated_records: list[BaseModel] = []

        for index, record in enumerate(records):
            try:
                validated_records.append(
                    self.validate(
                        data=record,
                        schema=schema,
                    )
                )

            except DataValidationError as exc:
                raise DataValidationError(
                    message=(
                        f"Validation failed for record "
                        f"at index {index}."
                    ),
                    errors=[
                        {
                            "record_index": index,
                            "errors": exc.errors,
                        }
                    ],
                ) from exc

        return validated_records

    # ------------------------------------------------------------------
    # Dataset validation
    # ------------------------------------------------------------------

    def validate_dataset(
        self,
        data: dict[str, Any],
        schema: Type[BaseModel],
    ) -> dict[str, Any]:
        """
        Validate a complete OVI dataset.

        Example:

            validated = validator.validate_dataset(
                data,
                CoursesSchema,
            )

        Returns:
            JSON-compatible validated dataset.
        """

        return self.validate_to_dict(
            data=data,
            schema=schema,
        )

    # ------------------------------------------------------------------
    # Safe validation
    # ------------------------------------------------------------------

    def is_valid(
        self,
        data: Any,
        schema: Type[BaseModel],
    ) -> bool:
        """
        Check whether data is valid without raising an exception.

        Returns:
            True  -> valid
            False -> invalid
        """

        try:
            self.validate(
                data=data,
                schema=schema,
            )

            return True

        except DataValidationError:
            return False

    # ------------------------------------------------------------------
    # Validation with error reporting
    # ------------------------------------------------------------------

    def validate_with_errors(
        self,
        data: Any,
        schema: Type[BaseModel],
    ) -> tuple[bool, BaseModel | None, list[dict[str, Any]]]:
        """
        Validate data and return the result without raising.

        Returns:

            (
                is_valid,
                validated_model,
                errors
            )
        """

        try:
            model = self.validate(
                data=data,
                schema=schema,
            )

            return True, model, []

        except DataValidationError as exc:
            return False, None, exc.errors
