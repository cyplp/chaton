import logging
import datetime
import os.path

from pyramid.view import view_config
from pyramid.threadlocal import get_current_registry
from pyramid.security import remember
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound

import couchdbkit
from couchdbkit.designer import push

import bcrypt

from chaton.models import User
from chaton.models import Video

logger = logging.getLogger('view')

settings = get_current_registry().settings

server = couchdbkit.Server(settings['couchdb.url'])
db = server.get_or_create_db(settings['couchdb.db'])

User.set_db(db)
Video.set_db(db)

here = os.path.dirname(__file__)
for view in ['video']:
    path = os.path.join(here, 'couchdb', '_design', view)
    push(path, db)


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

    return HTTPFound(location=request.route_path('home'), headers=headers)


@view_config(route_name='home', renderer='templates/logged.pt', logged=True)
def logged(request):
    videos = Video.view('video/all', limit=10,
                        descending=True,
                        skip=0)
    return {'videos': videos}

@view_config(route_name='upload', renderer='templates/upload.pt', logged=True, request_method="GET")
def upload(request):
    return {}


@view_config(route_name='upload', logged=True, request_method="POST")
def uploading(request):
    title = request.POST.get('title', '')
    description = request.POST.get('description', '')
    owner = request.session['username']
    userid = request.session['login']

    created = datetime.datetime.now()

    video = Video(title=title,
                  description=description,
                  owner=owner,
                  userid=userid,
                  created=created)
    video.save()

    #todo secu
    video.put_attachment(request.POST['file'].file, 'video', content_type="video/quicktime")

    return HTTPFound(location=request.route_path('video', id=video._id))

@view_config(route_name='video', renderer='templates/video.pt', logged=True, request_method="GET")
def video(request):
    try:
        video = Video.get(request.matchdict['id'])
    except couchdbkit.exceptions.ResourceNotFound:
        return HTTPNotFound()


    return {'video': video}



@view_config(route_name='vuser', renderer='templates/logged.pt', logged=True,)
def vuser(request):
    videos = Video.view('video/vuser', limit=10,
                        descending=True,
                        skip=0,
                        startkey=[request.matchdict['id'], {}],)
    return {'videos': videos}


@view_config(route_name='addtag', logged=True, request_method="POST")
def addtag(request):
    try:
        video = Video.get(request.matchdict['id'])
    except couchdbkit.exceptions.ResourceNotFound:
        return HTTPNotFound()

    tag = request.POST.get('tag', None)

    if tag:
        if tag not in video.tags:
            video.tags.append(tag)
            video.save()
    return HTTPFound(location=request.route_path('video', id=video._id))


@view_config(route_name='tag', renderer='templates/logged.pt', logged=True,)
def tag(request):
    videos = Video.view('video/tag', limit=10,
                        descending=True,
                        skip=0,
                        startkey=[request.matchdict['id'], {}],)
    return {'videos': videos}
