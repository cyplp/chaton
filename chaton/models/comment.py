import couchdbkit

class Comment(couchdbkit.Document):
    """
    """
    owner = couchdbkit.StringProperty()
    userid = couchdbkit.StringProperty()
    content = couchdbkit.StringProperty()
    created = couchdbkit.DateTimeProperty()
    videoid = couchdbkit.StringProperty()
