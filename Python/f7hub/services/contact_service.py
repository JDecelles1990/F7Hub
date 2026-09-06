"""Create the minimal active contact needed for a company-scoped ticket."""

from datetime import datetime, timezone
import sqlite3

from f7hub.repositories.company_repository import CompanyRepository
from f7hub.repositories.contact_repository import ContactRecord, ContactRepository


class ContactValidationError(ValueError):
    """Invalid quick-contact input; safe to display."""


class ContactCreationError(RuntimeError):
    """Contact persistence failed; safe to display."""


class ContactService:
    """Validate company identity and coordinate one atomic contact creation."""

    def __init__(self, repository: ContactRepository, companies: CompanyRepository):
        self._repository = repository
        self._companies = companies

    def create_contact(self, *, company_id: int, display_name: str,
                       email: str | None = None) -> ContactRecord:
        if type(company_id) is not int or not 1 <= company_id <= 2**63 - 1:
            raise ContactValidationError("Select a valid active company.")
        if not isinstance(display_name, str):
            raise ContactValidationError("Contact name must be text.")
        display_name = display_name.strip()
        if not display_name:
            raise ContactValidationError("Contact name is required.")
        if email is not None and not isinstance(email, str):
            raise ContactValidationError("Email must be text.")
        email = (email.strip() or None) if email is not None else None
        timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        try:
            with self._repository.transaction() as connection:
                company = self._companies.get_company(company_id, connection=connection)
                if company is None or not company.is_active:
                    raise ContactValidationError("The selected company is no longer available or active.")
                return self._repository.create_contact(
                    company_id=company_id, display_name=display_name, email=email,
                    is_active=1, created_at=timestamp, updated_at=timestamp,
                    connection=connection,
                )
        except (sqlite3.Error, OSError, RuntimeError) as error:
            raise ContactCreationError(
                "Could not create the contact. Your entered information is preserved."
            ) from error
