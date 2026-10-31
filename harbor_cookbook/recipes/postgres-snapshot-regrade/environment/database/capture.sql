-- One statement provides a consistent snapshot of all grading inputs.
-- Explicit columns, table names, and ordering keep the artifact deterministic.
SELECT jsonb_build_object(
    'schema_version', 1,
    'customers', (
        SELECT COALESCE(jsonb_agg(to_jsonb(row) ORDER BY id), '[]'::jsonb)
        FROM (SELECT id, name FROM public.customers) AS row
    ),
    'orders', (
        SELECT COALESCE(jsonb_agg(to_jsonb(row) ORDER BY id), '[]'::jsonb)
        FROM (SELECT id, customer_id, total_cents FROM public.orders) AS row
    ),
    'line_items', (
        SELECT COALESCE(jsonb_agg(to_jsonb(row) ORDER BY id), '[]'::jsonb)
        FROM (
            SELECT id, order_id, quantity, unit_price_cents FROM public.line_items
        ) AS row
    )
);
