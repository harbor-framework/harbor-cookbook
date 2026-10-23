The order totals in the PostgreSQL database are inconsistent with their line
items. Repair `public.orders.total_cents` so that every order's total equals
the sum of `quantity * unit_price_cents` for its line items. An order with no
line items must have a total of zero.

Use `psql`; the `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD`
environment variables are already configured. Inspect the schema and data
before making changes. Preserve every row and every column other than
`orders.total_cents`. Commit your changes before finishing.
