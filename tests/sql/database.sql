BEGIN;

-- Tables

CREATE TABLE Employee (
	person_id INTEGER NOT NULL, 
	name VARCHAR, 
	firstname VARCHAR, 
	login VARCHAR, 
	"order" INTEGER, 
	password VARCHAR, 
	company_id INTEGER,
	driving_license INTEGER,
	photo VARCHAR,
	resume VARCHAR,
	reflected VARCHAR, 
	PRIMARY KEY (person_id), 
	FOREIGN KEY(company_id) REFERENCES Company (company_id)
);

CREATE TABLE Company (
	company_id INTEGER NOT NULL, 
	name VARCHAR,
	PRIMARY KEY (company_id)
);

INSERT INTO company VALUES (1, 'Test Company 1');

INSERT INTO employee (person_id, name, firstname, login, password, driving_license, "order", resume, photo, company_id) VALUES
    (1, 'admin', 'admin', 'admin', 'root', 1, 1, NULL, NULL, NULL),
    (2, 'Tester', 'Tester', 'test_login', 'test_psswd', 0, 2, NULL, NULL, NULL),
    (3, 'Tester', 'Hired', 'hired_tester', 'hired_tester_psswd', 1, 3, NULL, NULL, 1);

COMMIT;
