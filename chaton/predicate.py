class LoggedPredicate(object):
    """
    """

    def __init__(self, val, config):
        self._val = val

    def text(self):
        return 'predicat on login : '+ str(self._val)

    phash = text

    def __call__(self,  context, request):
        return ('login' in request.session) == self._val

class IsAdminPredicate(object):
    """
    """

    def __init__(self, val, config):
        self._val = val

    def text(self):
        return 'predicat on admin : '+ str(self._val)

    phash = text

    def __call__(self,  context, request):
        return ('isAdmin' in request.session and \
                              request.session['isAdmin']) == self._val
