BEGIN;

INSERT INTO company VALUES (1, 'Test Company 1');

INSERT INTO employee (person_id, name, firstname, login, password, driving_license, company_id) VALUES
    (1, 'admin', 'admin', 'admin', 'root', 1, NULL),
    (2, 'Tester', 'Tester', 'test_login', 'test_psswd', 0, NULL),
    (3, 'Tester', 'Hired', 'hired_tester', 'hired_tester_psswd', 1, 1);

COMMIT;
