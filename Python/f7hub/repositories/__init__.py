"""Explicit SQLite persistence boundaries for F7Hub."""

from f7hub.repositories.company_repository import CompanyRecord, CompanyRepository
from f7hub.repositories.contact_repository import ContactRecord, ContactRepository
from f7hub.repositories.ticket_repository import (
    TicketNoteRecord,
    TicketRecord,
    TicketRepository,
    TicketStatusHistoryRecord,
    TicketTimelineEventRecord,
)


__all__ = (
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
