"""Read company, contact and category choices without GUI dependencies."""

from dataclasses import dataclass
import sqlite3

from f7hub.repositories.company_repository import CompanyRepository
from f7hub.repositories.contact_repository import ContactRepository
from f7hub.repositories.category_repository import CategoryRepository


@dataclass(frozen=True)
class TicketReferenceOption:
    """A canonical display label and its independent persistent identifier."""

    reference_id: int
    label: str


class TicketReferenceError(ValueError):
    """Reference choices are unavailable or the requested company is invalid."""


class TicketReferenceService:
    """Supply only the read operations needed by the ticket form."""

    def __init__(self, companies: CompanyRepository, contacts: ContactRepository,
                 categories: CategoryRepository):
        self._companies = companies
        self._contacts = contacts
        self._categories = categories

    def list_active_ticket_categories(self) -> tuple[TicketReferenceOption, ...]:
        try:
            return tuple(TicketReferenceOption(row.category_id, row.name)
                         for row in self._categories.list_categories(scope="TICKET", active_only=True))
        except sqlite3.Error as error:
            raise TicketReferenceError("Could not load ticket categories.") from error

    def list_active_companies(self) -> tuple[TicketReferenceOption, ...]:
        try:
            return tuple(TicketReferenceOption(row.company_id, row.name)
                         for row in self._companies.list_companies(active_only=True))
        except sqlite3.Error as error:
            raise TicketReferenceError("Could not load companies.") from error

    def list_active_contacts_for_company(self, company_id: int) -> tuple[TicketReferenceOption, ...]:
        if (isinstance(company_id, bool) or not isinstance(company_id, int)
                or not 1 <= company_id <= 2**63 - 1):
            raise TicketReferenceError("Select a valid active company.")
        try:
            company = self._companies.get_company(company_id)
            if company is None or not company.is_active:
                raise TicketReferenceError("The selected company is no longer available.")
            return tuple(TicketReferenceOption(row.contact_id, row.display_name)
                         for row in self._contacts.list_contacts_for_company(company_id)
                         if row.is_active)
        except sqlite3.Error as error:
            raise TicketReferenceError("Could not load contacts.") from error
