CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY,

    company_code TEXT COLLATE NOCASE UNIQUE,

    name TEXT NOT NULL
        CHECK (length(trim(name)) > 0),

    domain TEXT COLLATE NOCASE,
    phone TEXT,
    website_url TEXT,

    address_line1 TEXT,
    address_line2 TEXT,
    city TEXT,
    region TEXT,
    postal_code TEXT,
    country_code TEXT,

    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE company_notes (
    company_note_id INTEGER PRIMARY KEY,

    company_id INTEGER NOT NULL,

    note_text TEXT NOT NULL
        CHECK (length(trim(note_text)) > 0),

    is_pinned INTEGER NOT NULL DEFAULT 0
        CHECK (is_pinned IN (0, 1)),

    created_by TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON DELETE CASCADE
);

CREATE TABLE company_links (
    company_link_id INTEGER PRIMARY KEY,

    company_id INTEGER NOT NULL,

    link_type TEXT,

    label TEXT NOT NULL
        CHECK (length(trim(label)) > 0),

    url TEXT NOT NULL
        CHECK (length(trim(url)) > 0),

    sort_order INTEGER NOT NULL DEFAULT 0,

    created_at TEXT NOT NULL,

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON DELETE CASCADE
);

CREATE TABLE contacts (
    contact_id INTEGER PRIMARY KEY,

    company_id INTEGER,

    display_name TEXT NOT NULL
        CHECK (length(trim(display_name)) > 0),

    first_name TEXT,
    last_name TEXT,
    job_title TEXT,

    email TEXT COLLATE NOCASE,

    phone TEXT,
    mobile_phone TEXT,
    notes TEXT,

    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON DELETE SET NULL
);

CREATE INDEX idx_companies_name
    ON companies(name COLLATE NOCASE);

CREATE INDEX idx_companies_domain
    ON companies(domain);

CREATE INDEX idx_company_notes_company_created
    ON company_notes(
        company_id,
        created_at DESC
    );

CREATE INDEX idx_company_links_company_sort
    ON company_links(
        company_id,
        sort_order
    );

CREATE INDEX idx_contacts_company_name
    ON contacts(
        company_id,
        display_name COLLATE NOCASE
    );

CREATE INDEX idx_contacts_email
    ON contacts(email);
