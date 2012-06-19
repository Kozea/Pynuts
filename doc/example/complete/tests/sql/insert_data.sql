BEGIN;

INSERT INTO company VALUES (1, 'Test Company 1');

INSERT INTO employee VALUES (1, 'admin', 'admin', 'admin', 'root', NULL);
INSERT INTO employee VALUES (2, 'Tester', 'Tester', 'test_login', 'test_psswd', NULL);
INSERT INTO employee VALUES (3, 'Tester', 'Hired', 'hired_tester', 'hired_tester_psswd', 1);

COMMIT;
