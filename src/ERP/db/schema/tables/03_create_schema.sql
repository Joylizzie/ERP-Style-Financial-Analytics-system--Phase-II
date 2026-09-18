-- This is just at the initial stage of running, for muliptle period, DON"T drop this schema any more! #TODO 
DROP SCHEMA IF EXISTS ocean_stream CASCADE; 

CREATE SCHEMA IF NOT EXISTS ocean_stream;

ALTER USER ocean_user SET search_path  TO ocean_stream, public;