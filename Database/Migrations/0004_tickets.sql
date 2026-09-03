CREATE TABLE tickets (
    ticket_id INTEGER PRIMARY KEY,

    ticket_number TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(ticket_number)) > 0),

    ticket_type TEXT NOT NULL DEFAULT 'INCIDENT'
        CHECK (
            ticket_type IN (
                'INCIDENT',
                'SERVICE_REQUEST',
                'PROBLEM',
                'TASK'
            )
        ),

    status TEXT NOT NULL DEFAULT 'NEW'
        CHECK (
            status IN (
                'NEW',
                'OPEN',
                'IN_PROGRESS',
                'WAITING',
                'RESOLVED',
                'CLOSED',
                'CANCELLED'
            )
        ),

    priority TEXT NOT NULL DEFAULT 'MEDIUM'
        CHECK (
            priority IN (
                'LOW',
                'MEDIUM',
                'HIGH',
                'CRITICAL'
            )
        ),

    company_id INTEGER,
    contact_id INTEGER,
    category_id INTEGER,

    subject TEXT NOT NULL
        CHECK (length(trim(subject)) > 0),

    description TEXT,
    resolution TEXT,

    assigned_to TEXT,
    source TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    resolved_at TEXT,
    closed_at TEXT,

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON DELETE SET NULL,

    FOREIGN KEY (contact_id)
        REFERENCES contacts(contact_id)
        ON DELETE SET NULL,

    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE SET NULL,

    CHECK (
        resolved_at IS NULL
        OR status IN ('RESOLVED', 'CLOSED')
    ),

    CHECK (
        closed_at IS NULL
        OR status = 'CLOSED'
    )
);

CREATE TABLE ticket_notes (
    ticket_note_id INTEGER PRIMARY KEY,

    ticket_id INTEGER NOT NULL,

    note_type TEXT NOT NULL DEFAULT 'INTERNAL'
        CHECK (
            note_type IN (
                'INTERNAL',
                'PUBLIC',
                'WORKLOG',
                'RESOLUTION'
            )
        ),

    note_text TEXT NOT NULL
        CHECK (length(trim(note_text)) > 0),

    author_label TEXT,
    source TEXT,

    is_ai_generated INTEGER NOT NULL DEFAULT 0
        CHECK (is_ai_generated IN (0, 1)),

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id)
        ON DELETE CASCADE
);

CREATE TABLE ticket_status_history (
    ticket_status_history_id INTEGER PRIMARY KEY,

    ticket_id INTEGER NOT NULL,

    previous_status TEXT
        CHECK (
            previous_status IS NULL
            OR previous_status IN (
                'NEW',
                'OPEN',
                'IN_PROGRESS',
                'WAITING',
                'RESOLVED',
                'CLOSED',
                'CANCELLED'
            )
        ),

    new_status TEXT NOT NULL
        CHECK (
            new_status IN (
                'NEW',
                'OPEN',
                'IN_PROGRESS',
                'WAITING',
                'RESOLVED',
                'CLOSED',
                'CANCELLED'
            )
        ),

    reason TEXT,
    changed_by TEXT,
    changed_at TEXT NOT NULL,

    FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id)
        ON DELETE CASCADE,

    CHECK (
        previous_status IS NULL
        OR previous_status <> new_status
    )
);

CREATE TABLE ticket_timeline_events (
    ticket_timeline_event_id INTEGER PRIMARY KEY,

    ticket_id INTEGER NOT NULL,

    event_type TEXT NOT NULL
        CHECK (length(trim(event_type)) > 0),

    title TEXT NOT NULL
        CHECK (length(trim(title)) > 0),

    details TEXT,
    metadata_json TEXT,
    actor_label TEXT,

    occurred_at TEXT NOT NULL,

    FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_tickets_status_updated
    ON tickets(
        status,
        updated_at DESC
    );

CREATE INDEX idx_tickets_company_status
    ON tickets(
        company_id,
        status
    );

CREATE INDEX idx_tickets_contact_id
    ON tickets(contact_id);

CREATE INDEX idx_tickets_priority_status
    ON tickets(
        priority,
        status
    );

CREATE INDEX idx_tickets_category_id
    ON tickets(category_id);

CREATE INDEX idx_tickets_created_at
    ON tickets(created_at DESC);

CREATE INDEX idx_ticket_notes_ticket_created
    ON ticket_notes(
        ticket_id,
        created_at DESC
    );

CREATE INDEX idx_ticket_status_history_ticket_changed
    ON ticket_status_history(
        ticket_id,
        changed_at DESC
    );

CREATE INDEX idx_ticket_timeline_ticket_occurred
    ON ticket_timeline_events(
        ticket_id,
        occurred_at DESC
    );
