import couchdbkit

class Video(couchdbkit.Document):
    """
    """
    title = couchdbkit.StringProperty()
    description = couchdbkit.StringProperty()
    owner = couchdbkit.StringProperty()
    userid = couchdbkit.StringProperty()
    tags = couchdbkit.StringListProperty()
    comments = couchdbkit.ListProperty()
    created = couchdbkit.DateTimeProperty()
    #metadata = couchdbkit.DictProperty()
