# PostgreSQL 17.11; use the official image for database initialization.
FROM postgres:17-bookworm@sha256:858bb5e98eed02eb8cafbcdc007f9a65d1b613972028944a8ec2133ccaf80d27

COPY init.sql /docker-entrypoint-initdb.d/01-init.sql
COPY pg_hba.conf /etc/postgresql/recipe-pg_hba.conf
COPY capture.sql /opt/recipe/capture.sql
COPY --chmod=755 capture-state.sh /usr/local/bin/capture-state

RUN install -d -o postgres -g postgres -m 700 /snapshot
