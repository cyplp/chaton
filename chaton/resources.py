from fanstatic import Library
from fanstatic import Resource
from fanstatic import Group

from js.jquery import jquery

library = Library('resources', 'resources_src')

cssChaton = Resource(library, 'chaton.css')

uploadJS = Resource(library, 'upload.js', depends=[jquery])
uploadGroup = Group([uploadJS])

cssGroup =  Group([cssChaton])
