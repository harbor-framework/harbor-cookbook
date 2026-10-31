#!/bin/bash
set -euo pipefail

psql -X -v ON_ERROR_STOP=1 <<'SQL'
BEGIN;
UPDATE public.orders AS orders
SET total_cents = COALESCE((
    SELECT SUM(items.quantity * items.unit_price_cents)
    FROM public.line_items AS items
    WHERE items.order_id = orders.id
), 0);
COMMIT;
SQL
