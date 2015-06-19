# Copyright 2015 Vinicius Chiele. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mimetypes

from os.path import join, getsize, getmtime
from werkzeug.datastructures import Headers


class ApiDoc(object):
    def __init__(self, folder_path=None, url_path=None, app=None):
        self.folder_path = folder_path
        self.url_path = url_path
        self.base_url_path = None

        if self.folder_path is None:
            self.folder_path = 'apidoc'

        if self.url_path is None:
            self.url_path = '/apidoc'

        self.app = None

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        url = self.url_path

        if not self.url_path.endswith('/'):
            url += '/'

        app.add_url_rule(url, 'apidoc', self.__apidoc_view)
        app.add_url_rule(url + '<path:path>', 'apidoc', self.__apidoc_view)

        self.base_url_path = app.config.get('APIDOC_URL')

    def __apidoc_view(self, path=None):
        if not path:
            path = 'index.html'

        file_name = join(self.folder_path, path)

        if path == 'api_project.js' or path == 'api_project.json' and self.base_url_path:
            return self.__send_static_file(file_name)

        return self.app.send_static_file(file_name)

    def __send_static_file(self, file_name):
        file_name = join(self.app.static_folder, file_name)

        with open(file_name, 'rt') as file:
            data = file.read()

        data = self.__replace_url(data)

        headers = Headers()
        headers['Content-Length'] = getsize(file_name)

        response = self.app.response_class(data,
                                           mimetype=mimetypes.guess_type(file_name)[0],
                                           headers=headers,
                                           direct_passthrough=True)

        response.last_modified = int(getmtime(file_name))

        return response

    def __replace_url(self, data):
        i = data.find('"url"')

        if i == -1:
            return data

        start = data.find('"', i + 5) + 1
        end = data.find('"', start + 1)

        content = data[:start]
        content += self.base_url_path
        content += data[end:]

        return content
