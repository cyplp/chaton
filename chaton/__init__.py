from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.threadlocal import get_current_registry

from chaton.predicate import LoggedPredicate, IsAdminPredicate


my_session_factory = SignedCookieSessionFactory('itsaseekreet')

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.set_session_factory(my_session_factory)

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('upload', '/upload')
    config.add_route('video', '/video/{id}')
    config.add_route('vuser', '/vuser/{id}')

    get_current_registry().settings = settings

    for include in ['pyramid_mailer',
                    'pyramid_fanstatic',
                    'pyramid_chameleon',
                    'rebecca.fanstatic', ]:

        config.include(include)


    config.add_view_predicate('logged', LoggedPredicate)
    config.add_view_predicate('isAdmin', IsAdminPredicate)

    config.add_fanstatic_resources(['js.bootstrap.bootstrap',
                                    'js.bootstrap.bootstrap_theme',
                                    'css.fontawesome.fontawesome',
                                    ], r'.*\.pt')

    config.scan()
    return config.make_wsgi_app()
