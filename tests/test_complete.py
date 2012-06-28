# -*- coding: utf-8 -*-

# Copyright (C) 2011 Kozea
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Test for Pynuts (all the routes are tested)"""

import json
from flask import url_for

from pynuts.document import InvalidId
from pynuts.git import ConflictError

from . import (
    teardown_func, setup_func, setup_fixture as setup_module,
    teardown_fixture as teardown_module)
from .helpers import with_client, request
from complete.exception import NoPermission
from complete.application import app


class TestComplete(object):
    def setup(self):
        setup_func()

    def teardown(self):
        teardown_func()

    @with_client
    def test_login_post(self, client):
        """Test the login post."""
        with client.application.test_request_context():
            response = request(
                client.post, url_for('login_post'),
                data={'login': 'fake_login', 'passwd': ''})
            assert 'invalid credentials' in response.data
            response = request(
                client.post, url_for('login_post'),
                data={'login': 'admin', 'passwd': 'root'})

    @with_client
    def test_logout(self, client):
        """Test the logout."""
        with client.application.test_request_context():
            response = request(client.get, url_for('logout'))
            assert 'Login required' in response.data
            response = request(client.get, '/', status_code=403)

    @with_client
    def test_employee_create_fields(self, client):
        """Check employee create fields."""
        with client.application.test_request_context():
            response = request(client.get, url_for('create_employee'))
            assert 'name="login"' in response.data
            assert 'name="password"' in response.data
            assert 'name="name"' in response.data
            assert 'name="firstname' in response.data
            assert 'name="company"' in response.data

    @with_client
    def test_create_employee(self, client):
        """Create an employee."""
        with client.application.test_request_context():
            response = request(
                client.post, url_for('create_employee'),
                data={'login': 'Tester', 'password': 'test', 'name': 'Tester',
                      'firstname': 'Tester'})
            assert 'Tester Tester' in response.data
            response = request(
                client.post, url_for('create_employee'),
                data={'login': '', 'password': '', 'name': '', 'firstname': ''})
            assert 'This field is required' in response.data

    @with_client
    def test_update_fields(self, client):
        """Check employee update fields"""
        with client.application.test_request_context():
            response = request(client.get, url_for('update_employee'))
            assert 'name="name"' in response.data
            assert 'name="firstname' in response.data
            assert 'name="company"' in response.data

    @with_client
    def test_update_employee(self, client):
        """Update an employee."""
        with client.application.test_request_context():
            response = request(client.get, url_for('logout'))
            response = request(
                client.post, url_for('login_post'),
                data={'login': 'test_login', 'password': 'test_psswd'})
            response = request(
                client.post, url_for('update_employee', person_id=2),
                data={'firstname': 'Updated', 'name': 'Tester'})
            assert 'Updated Tester' in response.data

    @with_client
    def test_delete_confirm(self, client):
        """Check the delete confimation."""
        with client.application.test_request_context():
            response = request(client.get, url_for('delete_employee', person_id=2))
            assert 'Do you really want to delete '
            '<strong>Tester Tester</strong>?' in response.data

    @with_client
    def test_delete_employee(self, client):
        """Delete an employee."""
        with client.application.test_request_context():
            response = request(
                client.post, url_for('delete_employee', person_id=2))
            assert 'Tester Tester' not in response.data

    @with_client
    def test_employee_list(self, client):
        """Check the employee list."""
        with client.application.test_request_context():
            response = request(client.get, url_for('employees'))
            assert 'Tester Tester' in response.data

    @with_client
    def test_employee_table(self, client):
        """Check the employee table."""
        with client.application.test_request_context():
            response = request(client.get, url_for('table_employees'))
            assert 'Tester Tester' in response.data

    @with_client
    def test_company_create_fields(self, client):
        """Check company create fields."""
        with client.application.test_request_context():
            response = request(client.get, url_for('create_company'))
            assert 'name="name"' in response.data
            assert 'name="employees"' in response.data

    @with_client
    def test_company_list(self, client):
        """Test the company list."""
        with client.application.test_request_context():
            response = request(client.get, url_for('companies'))
            assert 'Test Company 1' in response.data

    @with_client
    def test_create_employee_in_company(self, client):
        """Create employee with company."""
        with client.application.test_request_context():
            response = request(
                client.post, url_for('create_employee'),
                data={'login': 'Tester', 'password': 'test', 'firstname': 'Hired',
                      'name': 'Tester2', 'company': '1'})
            assert 'Hired Tester2' in response.data

    @with_client
    def test_check_company_have_employees(self, client):
        """Check company's employees."""
        with client.application.test_request_context():
            response = request(client.get, url_for('read_company', company_id=1))
            assert 'Hired Tester' in response.data

    @with_client
    def test_check_employee_in_company(self, client):
        """Check employee's company."""
        with client.application.test_request_context():
            response = request(client.get, url_for('read_employee', person_id=3))
            assert 'Test Company 1' in response.data

    @with_client
    def test_edit_template(self, client):
        """Test the edit template."""
        with client.application.test_request_context():
            response = request(
                client.get, url_for(
                    'edit_employee_report', person_id=1))
            assert 'EMPLOYEE\'S IDENTITY' in response.data
            assert '{{ field.label.text }}' in response.data

    @with_client
    def test_edit_template_post(self, client):
        """Test the edit template."""
        with client.application.test_request_context():
            response = request(
                client.post,
                url_for(
                    'edit_employee_report', person_id=1,
                    version='370fc6c4f1cf798e954791d7d9bbd169afabca71'),
                data={
                    'document': 'new template',
                    'message': 'Update new template',
                    '_old_commit': ''})
            assert 'The document was saved.' in response.data
            assert 'Employee List' in response.data
            response = request(
                client.post,
                url_for(
                    'edit_employee_report', person_id=1,
                    version='370fc6c4f1cf798e954791d7d9bbd169afabca71'),
                data={
                    'document': 'new template',
                    'message': 'Update new template',
                    '_old_commit': '370fc6c4f1cf798e954791d7d9bbd169afabca71'})
            assert 'A conflict happened.' in response.data

    @with_client
    def test_archive_employee_report(self, client):
        with client.application.test_request_context():
            response = request(
                client.post, url_for('archive_employee_report', person_id=1),
                data={'document': 'new template',
                      'message': 'Update new template',
                      '_old_commit': ''})
            assert 'The report was sucessfully archived.' in response.data

    @with_client
    def test_html_employee(self, client):
        """Test the HTML template."""
        with client.application.test_request_context():
            response = request(
                client.get, url_for('html_employee', person_id=1))
            assert 'EMPLOYEE\'S IDENTITY' in response.data

    @with_client
    def test_archived_html_employee(self, client):
        """Test the HTML template archive."""
        with client.application.test_request_context():
            response = request(
                client.get, url_for('archived_html_employee', person_id=1))
            assert 'EMPLOYEE\'S IDENTITY' in response.data

    @with_client
    def test_pdf_employee(self, client):
        """Test the PDF generation."""
        with client.application.test_request_context():
            response = request(
                client.get, url_for('pdf_employee', person_id=1),
                content_type='application/pdf')
            assert '%PDF' in response.data[:4]

    @with_client
    def test_archived_pdf_employee(self, client):
        """Test the PDF generation archive."""
        with client.application.test_request_context():
            response = request(
                client.get, url_for('archived_pdf_employee', person_id=1),
                content_type='application/pdf')
            assert '%PDF' in response.data[:4]

    @with_client
    def test_pynuts_static(self, client):
        """Test the pynuts static route."""
        with client.application.test_request_context():
            request(client.get,
                    url_for('_pynuts-static', filename='javascript/save.js'),
                    content_type='application/x-javascript')

    @with_client
    def test_pynuts_resource(self, client):
        """Test the pynuts resource route."""
        with client.application.test_request_context():
            request(client.get,
                    '/_pynuts/resource/EmployeeDoc/1'
                    '/370fc6c4f1cf798e954791d7d9bbd169afabca71/logo.png',
                    content_type='image/png')

    @with_client
    def test_rights(self, client):
        """Test for rights."""
        with client.application.test_request_context():
            request(client.get, url_for('test_rights'))
            request(client.get, url_for('logout'))
            try:
                request(client.get, url_for('test_rights'))
            except NoPermission:
                return
        raise StandardError('This test must raise NoPermission')

    @with_client
    def test_update_content(self, client):
        """Test the update_content method."""
        with client.application.test_request_context():
            response = request(client.post, url_for('_pynuts-update_content'),
                data=json.dumps({
                        "data": [{
                            "part": "comments",
                            "document_type": "EmployeeDoc",
                            "document_id": "1",
                            "version": "",
                            "content": "comment test"
                        }, {
                            "part": "info",
                            "document_type": "EmployeeDoc",
                            "document_id": "1",
                            "version": "",
                            "content": "info test"}
                        ],
                        "message": None,
                        "author": None,
                        "author_email": None
                    }), data_content_type='application/json',
                        content_type='application/json')
            assert "document" in response.data

    def test_InvalidId(self):
        """Test InvalidId exception."""
        class EmployeeDoc(app.Document):
            document_id_template = '/'
        try:
            EmployeeDoc.create()
        except InvalidId:
            return
        raise StandardError('This test must raise InvalidId')

    @with_client
    def test_test_endpoint(self, client):
        """Test the endpoint."""
        with client.application.test_request_context():
            response = request(
                client.get, url_for('test_endpoint', company_id=1))
            assert 'Test Company 1' in response.data

    @with_client
    def test_edit_image(self, client):
        """Test the endpoint."""
        filename = 'tests/dump/static/img/test.png'
        with client.application.test_request_context():
            response = request(
                client.get, url_for('edit_image', person_id=1))
            assert 'form' in response.data
        with client.application.test_request_context():
            with open(filename) as image_file:
                response = request(
                    client.post, url_for('edit_image', person_id=1),
                    data={'image': image_file})

    @with_client
    def test_conflict_error(self, client):
        """Test the endpoint."""
        filename = 'tests/dump/static/img/test.png'

        class EmployeeDoc(app.Document):
            pass

        content1 = EmployeeDoc(1).get_content('logo.png')
        content2 = EmployeeDoc(1).get_content('logo.png')
        try:
            content1.write(open(filename).read())
            content2.write(open(filename).read())
        except ConflictError:
            return
        raise StandardError('This test must raise ConflictError')
