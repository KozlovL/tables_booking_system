#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "prod_db" <<-EOSQL
    CREATE ROLE root LOGIN;
    CREATE DATABASE root;
EOSQL
