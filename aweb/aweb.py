import json

URL_DICT = dict()


def route(url):
    def set_url(func):
        URL_DICT[url] = func

        def call_func(*args, **kwargs):
            return func(*args, **kwargs)

        return call_func

    return set_url


class HttpResponse(object):
    def __init__(self, data):
        self.data = data


class JsonResponse(object):
    def __init__(self, data):
        self.data = data


@route('/')
def index(request):
    return HttpResponse({'code': 123})


@route('/index')
def index(request):
    print(request.get('data'))
    return JsonResponse({'code': 123})


def application(environ, start_response):
    path = environ['PATH_INFO']
    if response := URL_DICT.get(path, None):
        data = ''
        flag = False
        for i in environ['REQUEST']:
            if i == '':
                flag = True
            if flag:
                data += i
        j = eval(data)
        res = response({'data': j})
        if type(res) == HttpResponse:
            start_response('200 OK', [('Content-Type', ' text/plain; charset=UTF-8')])
        elif type(res) == JsonResponse:
            start_response('200 OK', [('Content-Type', ' application/json; charset=UTF-8')])
        else:
            start_response('200 OK', [('Content-Type', ' text/html; charset=UTF-8')])
        return json.dumps(res.data)
    else:
        start_response('404 Not Found', [('Content-Type', ' application/json; charset=UTF-8')])
        return '{"code": 404}'
