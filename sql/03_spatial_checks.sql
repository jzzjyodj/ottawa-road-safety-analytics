-- Validate spatial columns: latitude/longitude range, geometry validity.
-- TODO: confirm coordinate column names after schema inspection.

-- SELECT COUNT(*) FILTER (WHERE latitude NOT BETWEEN 45.0 AND 46.0) AS out_of_range_lat
-- FROM raw_collisions;
