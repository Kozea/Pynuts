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

"""
Helpers for tests, with definition of decorator and function.

"""
from complete import application
from complete import files
from functools import wraps


def with_client(function):
    """Create the test_client."""
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        """Decorator for the client login."""
        client = application.app.test_client()
        application.app.add_upload_sets(files.upload_sets())
        client.post('login', data={'login': 'admin', 'password': 'root'})
        return function(self, client=client, *args, **kwargs)
    return wrapper


def request(method, route, status_code=200, content_type='text/html',
            data=None, data_content_type=None, follow_redirects=True):
    """
    Create the test_client  and check status code and content_type.
    """
    response = method(route, content_type=data_content_type, data=data,
                      follow_redirects=follow_redirects)
    assert response.status_code == status_code
    assert content_type in response.content_type
    return response
