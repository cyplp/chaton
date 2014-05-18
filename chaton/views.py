# -*- coding: utf-8 -*-
import logging
import datetime
import os.path

import magic

from pyramid.view import view_config
from pyramid.threadlocal import get_current_registry
from pyramid.security import remember
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound

import couchdbkit
from couchdbkit.designer import push

import bcrypt

from chaton.models import User
from chaton.models import Video
from chaton.models import Comment

logger = logging.getLogger('view')

settings = get_current_registry().settings

server = couchdbkit.Server(settings['couchdb.url'])
db = server.get_or_create_db(settings['couchdb.db'])

User.set_db(db)
Video.set_db(db)
Comment.set_db(db)

here = os.path.dirname(__file__)
for view in ['video', 'comment']:
    path = os.path.join(here, 'couchdb', '_design', view)
    push(path, db)


def computeSkip(request):
    limit = 20
    page = int(request.GET.get('page', 0))
    skip = page * limit

    return skip, limit

def computeNextAndPrevious(request, view):
    limit = 20
    page = int(request.GET.get('page', 0))
    skip = page * limit

    previous = page is not 0
    following = skip + limit < view.total_rows

    return previous, following

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

    if 'previous' in request.session:
        if request.session['previous']:
            url = request.session['previous']
            del(request.session['previous'])
            return HTTPFound(location=url, headers=headers)

    return HTTPFound(location=request.route_path('home'), headers=headers)


@view_config(route_name='home', renderer='templates/logged.pt', logged=True)
def logged(request):
    skip, limit = computeSkip(request)

    videos = Video.view('video/all', limit=limit,
                        descending=True,
                        skip=skip)


    previous, following = computeNextAndPrevious(request, videos)

    return {'videos': videos, 'previous': previous, 'following': following}

@view_config(route_name='upload', renderer='templates/upload.pt', logged=True, request_method="GET")
def upload(request):
    return {}


@view_config(route_name='upload', logged=True, request_method="POST")
def uploading(request):
    title = request.POST.get('title', 'Sans titre')
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

    mime = magic.from_buffer(request.POST['file'].file.read(1024), mime=True)
    request.POST['file'].file.seek(0)

    #todo secu ???
    video.put_attachment(request.POST['file'].file, 'video', content_type=mime)
    return HTTPFound(location=request.route_path('video', id=video._id))

@view_config(route_name='video', renderer='templates/video.pt', logged=True, request_method="GET")
def video(request):
    try:
        video = Video.get(request.matchdict['id'])
    except couchdbkit.exceptions.ResourceNotFound:
        return HTTPNotFound()

    comments = Comment.view('comment/video',
                            descending=True,
                            skip=0,
                            startkey=[request.matchdict['id'], {}],
                            endkey=[request.matchdict['id']]
                            )

    return {'video': video, 'comments': comments}

@view_config(route_name='delete', logged=True, request_method="GET")
def delete(request):
    try:
        video = Video.get(request.matchdict['id'])
    except couchdbkit.exceptions.ResourceNotFound:
        return HTTPNotFound()

    video.delete()


    return HTTPFound(location=request.route_path("home"))


@view_config(route_name='vuser', renderer='templates/videos.pt', logged=True,)
def vuser(request):
    skip, limit = computeSkip(request)

    videos = Video.view('video/vuser', limit=limit,
                        descending=True,
                        skip=skip,
                        startkey=[request.matchdict['id'], {}],
                        endkey=[request.matchdict['id']])

    previous, following = computeNextAndPrevious(request, videos)

    return {'videos': videos, 'previous': previous, 'following': following}


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


@view_config(route_name='tag', renderer='templates/videos.pt', logged=True,)
def tag(request):

    skip, limit = computeSkip(request)

    videos = Video.view('video/tag', limit=limit,
                        descending=True,
                        skip=skip,
                        startkey=[request.matchdict['id'], {}],
                        endkey=[request.matchdict['id']])

    previous, following = computeNextAndPrevious(request, videos)
    return {'videos': videos, 'previous': previous, 'following': following}


@view_config(route_name="myaccount", renderer="templates/myaccount.pt", logged=True, request_method="GET")
def myaccount(request):
    try:
        user = User.get(request.session['login'])
    except couchdbkit.exceptions.ResourceNotFound:
        logger.info("%s unknown", request.session['login'])
        return HTTPFound(location=request.route_path('home'))

    return {'user': user}

@view_config(route_name="myaccount", logged=True, request_method="POST")
def updatemyaccount(request):
    try:
        user = User.get(request.session['login'])
    except couchdbkit.exceptions.ResourceNotFound:
        logger.info("%s unknown", request.session['login'])
        return HTTPFound(location=request.route_path('home'))

    password = request.POST.get('password', None)

    if not password:
        logger.info("no password")
        return HTTPFound(location=request.route_path('home'))

    new = request.POST.get('new', None)
    retype = request.POST.get('retype', None)

    if not new:
        logger.info("no new")
        return HTTPFound(location=request.route_path('home'))

    if new != retype:
        logger.info("new != type")
        return HTTPFound(location=request.route_path('home'))


    if bcrypt.hashpw(password.encode('utf-8'),
                     user.password) != user.password:
        logger.info("password false")

        return HTTPFound(location=request.route_path('home'))


    user.password = bcrypt.hashpw(new, bcrypt.gensalt())
    user.save()

    return HTTPFound(location=request.route_path('myaccount'))

@view_config(route_name='addcomment', logged=True, request_method="POST")
def addcomment(request):
    try:
        video = Video.get(request.matchdict['id'])
    except couchdbkit.exceptions.ResourceNotFound:
        return HTTPNotFound()

    commentContent = request.POST.get('comment', None)

    if commentContent:

        now = datetime.datetime.now()

        comment = Comment(owner=request.session['username'],
                          userid=request.session['login'],
                          created=now,
                          videoid=request.matchdict['id'],
                          content=commentContent.strip(),
                          )
        comment.save()

        video.comments.append(comment._id)
        video.save()

    return HTTPFound(location=request.route_path('video', id=video._id))


@view_config(route_name='myvideos', renderer='templates/logged.pt', logged=True,)
def myvideos(request):
    skip, limit = computeSkip(request)


    videos = Video.view('video/vuser', limit=limit,
                        descending=True,
                        skip=skip,
                        startkey=[request.session['login'], {}],
                        endkey=[request.session['login']])

    previous, following = computeNextAndPrevious(request, videos)

    return {'videos': videos, 'previous': previous, 'following': following}


@view_config(route_name='stream', logged=True, request_method="GET")
def stream(request):
    try:
        Video.get(request.matchdict['id'])
    except couchdbkit.exceptions.ResourceNotFound:
        return HTTPNotFound()
    #body = video.fetch_attachment('video', stream=True)

    #response = Response(body_file=body,)
    #return response

    response = request.response
    headers = response.headers

    headers['X-Accel-Redirect'] =  str('/couch/%s/video' % request.matchdict['id'])

    return response


@view_config(route_name='video', logged=False)
@view_config(route_name='addtag', logged=False)
@view_config(route_name='tag', logged=False,)
@view_config(route_name='addcomment', logged=False)
@view_config(route_name='myvideos', logged=False)
@view_config(route_name="logout", logged=False)
@view_config(route_name='stream', logged=False)
@view_config(route_name='upload', logged=False)
@view_config(route_name="myaccount", logged=False)
def ooops(request):
    request.session['previous'] = request.url
    return HTTPFound(location=request.route_path('home'))

@view_config(route_name="logout", logged=True)
def logout(request):
    headers = forget(request)
    del(request.session['username'])
    del(request.session['login'])
    del(request.session['isAdmin'])

    return HTTPFound(location=request.route_path("home"), headers=headers)
