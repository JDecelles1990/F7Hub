"""Create the minimal active company needed to continue a ticket draft."""

from datetime import datetime, timezone
import sqlite3

from f7hub.repositories.company_repository import CompanyRecord, CompanyRepository


class CompanyValidationError(ValueError):
    """Company input is invalid."""


class CompanyCreationError(RuntimeError):
    """Company persistence failed; safe to display to the technician."""


class CompanyService:
    """Validate company identity and delegate one atomic creation to persistence."""

    def __init__(self, repository: CompanyRepository):
        self._repository = repository

    def create_company(self, *, name: str) -> CompanyRecord:
        if not isinstance(name, str):
            raise CompanyValidationError("Company name must be text.")
        name = name.strip()
        if not name:
            raise CompanyValidationError("Company name is required.")
        timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        try:
            return self._repository.create_company(
                name=name, is_active=1, created_at=timestamp, updated_at=timestamp,
            )
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise CompanyCreationError(
                "Could not create the company. Your entered information is preserved."
            ) from error
