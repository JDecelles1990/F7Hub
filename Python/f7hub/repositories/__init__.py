"""Explicit SQLite persistence boundaries for F7Hub."""

from f7hub.repositories.company_repository import CompanyRecord, CompanyRepository
from f7hub.repositories.contact_repository import ContactRecord, ContactRepository
from f7hub.repositories.category_repository import CategoryRecord, CategoryRepository
from f7hub.repositories.ticket_repository import (
    TicketNoteRecord,
    TicketRecord,
    TicketRepository,
    TicketStatusHistoryRecord,
    TicketTimelineEventRecord,
)


__all__ = (
    "CategoryRecord",
    "CategoryRepository",
    "CompanyRecord",
    "CompanyRepository",
    "ContactRecord",
    "ContactRepository",
    "TicketNoteRecord",
    "TicketRecord",
    "TicketRepository",
    "TicketStatusHistoryRecord",
    "TicketTimelineEventRecord",
)
