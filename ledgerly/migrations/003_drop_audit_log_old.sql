-- 003_drop_audit_log_old.sql — applied to production 2024-11-02.
-- Destructive. Reviewed by DBA (ticket OPS-412). Never re-run or edit.
DROP TABLE IF EXISTS audit_log_old;
