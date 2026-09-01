CREATE SCHEMA IF NOT EXISTS ocean_stream;

ALTER USER ocean_user SET search_path  TO ocean_stream, public;