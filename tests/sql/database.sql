BEGIN;

-- Tables

CREATE TABLE "Employee" (
	person_id INTEGER NOT NULL, 
	name VARCHAR, 
	firstname VARCHAR, 
	login VARCHAR, 
	password VARCHAR, 
	company_id INTEGER, 
	reflected VARCHAR, 
	PRIMARY KEY (person_id), 
	FOREIGN KEY(company_id) REFERENCES "Company" (company_id)
);

CREATE TABLE "Company" (
	company_id INTEGER NOT NULL, 
	name VARCHAR, 
	PRIMARY KEY (company_id)
);

COMMIT;
