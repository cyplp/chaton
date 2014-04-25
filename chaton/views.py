import logging

from pyramid.view import view_config
from pyramid.threadlocal import get_current_registry
from pyramid.security import remember
from pyramid.httpexceptions import HTTPFound

#from pyramid.httpexceptions import HTTPNotFound

import couchdbkit
#from couchdbkit.designer import push

import bcrypt

from chaton.models.user import User

logger = logging.getLogger('view')

settings = get_current_registry().settings

server = couchdbkit.Server(settings['couchdb.url'])
db = server.get_or_create_db(settings['couchdb.db'])

User.set_db(db)


@view_config(route_name='home', renderer='templates/home.pt', logged=False)
def home(request):
    login = request.POST.get('login', '')
    return {'project': 'chaton',
            'login': login}

@view_config(route_name='home', renderer='templates/home.pt', request_method="POST", logged=False)
def signin(request):
    login = request.POST.get('login', '')
    password = request.POST.get('password', '')

    if not login or not password:
        logger.info("empty submit")
        return HTTPFound(location=request.route_path('home'))

    try:
        user = User.get(login)
    except couchdbkit.exceptions.ResourceNotFound:
        logger.info("%s unknown", login)
        return HTTPFound(location=request.route_path('home'))

    if bcrypt.hashpw(password.encode('utf-8'),
                     user.password) != user.password:

        return HTTPFound(location=request.route_path('home'))

    request.session.flash(u"welcome %s, you are logged" % user.name)

    headers = remember(request, user._id)
    request.session['username'] = user.name
    request.session['login'] = user._id
    request.session['isAdmin'] = user.isAdmin
    print dir(request.session)
    request.session.save()

    return HTTPFound(location=request.route_path('home'), headers=headers)


@view_config(route_name='home', renderer='templates/logged.pt', logged=True)
def logged(request):
    return {}
