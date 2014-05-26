from fanstatic import Library
from fanstatic import Resource
from fanstatic import Group

from js.jquery import jquery
from js.jquery_fileupload import jquery_fileupload

library = Library('resources', 'resources_src')

cssChaton = Resource(library, 'chaton.css')

uploadJS = Resource(library, 'upload.js', depends=[jquery, jquery_fileupload])
uploadGroup = Group([uploadJS])

cssGroup =  Group([cssChaton])
