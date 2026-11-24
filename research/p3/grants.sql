-- Apply only as postgres after creating dedicated bandzingest role.
-- No permissions on public journal tables are granted here.
BEGIN;
REVOKE ALL ON SCHEMA bandz_ingest FROM PUBLIC;
GRANT USAGE ON SCHEMA bandz_ingest TO bandzingest;
GRANT SELECT ON bandz_ingest.sources TO bandzingest;
GRANT SELECT, INSERT ON bandz_ingest.deliveries TO bandzingest;
GRANT UPDATE (status,error_code) ON bandz_ingest.deliveries TO bandzingest;
GRANT SELECT, INSERT ON bandz_ingest.events, bandz_ingest.delivery_events TO bandzingest;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA bandz_ingest TO bandzingest;
COMMIT;
