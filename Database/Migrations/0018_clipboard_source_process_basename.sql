-- CP02-S3: opt-in original-target executable basename on genuine Events only.
-- NULL preserves legacy/unavailable attribution. No backfill, rebuild or index.
ALTER TABLE clipboard_capture_events ADD COLUMN source_process_basename TEXT
    CHECK (source_process_basename IS NULL OR (
        typeof(source_process_basename) = 'text'
        AND length(source_process_basename) BETWEEN 5 AND 255
        AND length(CAST(source_process_basename AS BLOB)) <= 1020
        AND substr(source_process_basename, -4) = '.exe'
        AND substr(source_process_basename, 1, 1) NOT IN (' ', '.')
        AND instr(source_process_basename, char(0)) = 0
        AND source_process_basename NOT GLOB '*[<>:"/\|?*]*'
        -- Cc, Cf, Cs, Zl and Zp ranges from the domain profile (Unicode 16.0.0).
        AND source_process_basename NOT GLOB ('*[' || char(1) || '-' || char(31)
            || char(127) || '-' || char(159)
            || char(173)
            || char(1536) || '-' || char(1541)
            || char(1564)
            || char(1757)
            || char(1807)
            || char(2192) || '-' || char(2193)
            || char(2274)
            || char(6158)
            || char(8203) || '-' || char(8207)
            || char(8232) || '-' || char(8238)
            || char(8288) || '-' || char(8292)
            || char(8294) || '-' || char(8303)
            || char(55296) || '-' || char(57343)
            || char(65279)
            || char(65529) || '-' || char(65531)
            || char(69821)
            || char(69837)
            || char(78896) || '-' || char(78911)
            || char(113824) || '-' || char(113827)
            || char(119155) || '-' || char(119162)
            || char(917505)
            || char(917536) || '-' || char(917631) || ']*')
    ));
