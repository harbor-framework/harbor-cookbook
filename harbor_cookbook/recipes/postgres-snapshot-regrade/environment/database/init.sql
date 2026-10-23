CREATE TABLE public.customers (
    id integer PRIMARY KEY,
    name text NOT NULL
);

CREATE TABLE public.orders (
    id integer PRIMARY KEY,
    customer_id integer NOT NULL REFERENCES public.customers(id),
    total_cents integer NOT NULL CHECK (total_cents >= 0)
);

CREATE TABLE public.line_items (
    id integer PRIMARY KEY,
    order_id integer NOT NULL REFERENCES public.orders(id),
    quantity integer NOT NULL CHECK (quantity > 0),
    unit_price_cents integer NOT NULL CHECK (unit_price_cents >= 0)
);

INSERT INTO public.customers VALUES (1, 'Ada'), (2, 'Grace');
INSERT INTO public.orders VALUES
    (101, 1, 0), (102, 2, 999), (103, 1, 77), (104, 2, 1500);
INSERT INTO public.line_items VALUES
    (1, 101, 2, 1200),
    (2, 101, 1, 100),
    (3, 102, 1, 2999),
    (4, 102, 2, 250),
    (5, 104, 3, 500);

CREATE ROLE agent LOGIN PASSWORD 'agent';
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE orders FROM PUBLIC;
GRANT CONNECT ON DATABASE orders TO agent;
GRANT USAGE ON SCHEMA public TO agent;
GRANT SELECT ON public.customers, public.orders, public.line_items TO agent;
GRANT UPDATE (total_cents) ON public.orders TO agent;
