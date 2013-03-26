#! /usr/bin/env python
from wsgiref.simple_server import make_server
import urlparse
import simplejson
import db, recipes

dispatch = {
    '/' : 'index',
    '/recipes' : 'recipes',
    '/inventory' : 'inventory',
    '/liquor' : 'liquor',
    '/form' : 'form',
    '/recv' : 'recv',
    '/rpc'  : 'dispatch_rpc'
}

html_headers = [('Content-type', 'text/html')]

class SimpleApp(object):
    def __call__(self, environ, start_response):

        path = environ['PATH_INFO']
        fn_name = dispatch.get(path, 'error')

        # retrieve 'self.fn_name' where 'fn_name' is the
        # value in the 'dispatch' dictionary corresponding to
        # the 'path'.
        fn = getattr(self, fn_name, None)

        if fn is None:
            start_response("404 Not Found", html_headers)
            return ["No path %s found" % path]

        return fn(environ, start_response)
            
    def index(self, environ, start_response):

        data = """\
        Table of contents:<br>
        <a href='recipes'>List of Recipes</a><br>
        <a href='inventory'>Inventory</a><br>
        <a href='liquor'>Liquor Types</a><br>
        <a href='form'>Volume Converter</a><br>
        """

        start_response('200 OK', list(html_headers))
        return [data]
        
    def recipes(self, environ, start_response):
        content_type = 'text/html'
        data = """\
        <a href='/'>Return to Index</a><p>
        """

        for recipe in db.get_all_recipes():
            data += "<li %s: " % recipe.name
            if not recipe.need_ingredients():
                data += "AVAILABLE"
            else:
                data += "NEED "
                for (l, a) in recipe.need_ingredients():
                    data += "%s - %sml, " % (l, a)
                
        start_response('200 OK', list(html_headers))
        return [data]

    def error(self, environ, start_response):
        status = "404 Not Found"
        content_type = 'text/html'
        data = "Couldn't find your stuff."
       
        start_response('200 OK', list(html_headers))
        return [data]

    def inventory(self, environ, start_response):
        content_type = 'text/html'
        data = """\
        <a href='/'>Return to Index</a><p>
        """

        for (m, f) in db._inventory_db:
            data += "<li> %s - %s - %s" % (m, f, db._inventory>db[(m, f)])
        
        start_response('200 OK', list(html_headers))
        return [data]

    def liquor(self, environ, start_response):
        content_type = 'text/html'
        data = """\
        <a href='/'>Return to Index</a><p>
        """

        for (m, f, g) in db._bottle_types_db:
            data += "<li> %s - %s - %s" % (m, f, g)
        data += "</ul>"

        start_response('200 OK', list(html_headers))
        return [data]

    def form(self, environ, start_response):
        data = form()

        start_response('200 OK', list(html_headers))
        return [data]
   
    def recv(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        origAmount = float(results['amount'][0])
        measurement = results['measurement'][0]
        amount = origAmount

        if measurement == "oz":
            amount *= 29.5735
        elif measurement == "gal":
            amount *= 3785.41
        elif measurement == "lt":
            amount *= 1000.0
        else:
            raise Exception("Unknown unit input: ", measurement)
            return 0

        content_type = 'text/html'
        data = "%s %s = %s ml<br><br> <a href='/'>Return to Index</a>" % (origAmount, measurement, amount)

        start_response('200 OK', list(html_headers))
        return [data]

    def dispatch_rpc(self, environ, start_response):
        # POST requests deliver input data via a file-like handle,
        # with the size of the data specified by CONTENT_LENGTH;
        # see the WSGI PEP.
        
        if environ['REQUEST_METHOD'].endswith('POST'):
            body = None
            if environ.get('CONTENT_LENGTH'):
                length = int(environ['CONTENT_LENGTH'])
                body = environ['wsgi.input'].read(length)
                response = self._dispatch(body) + '\n'
                start_response('200 OK', [('Content-Type', 'application/json')])

                return [response]

        # default to a non JSON-RPC error.
        status = "404 Not Found"
        content_type = 'text/html'
        data = "Couldn't find your stuff."
       
        start_response('200 OK', list(html_headers))
        return [data]

    def _decode(self, json):
        return simplejson.loads(json)

    def _dispatch(self, json):
        rpc_request = self._decode(json)

        method = rpc_request['method']
        params = rpc_request['params']
        
        rpc_fn_name = 'rpc_' + method
        fn = getattr(self, rpc_fn_name)
        result = fn(*params)

        response = { 'result' : result, 'error' : None, 'id' : 1 }
        response = simplejson.dumps(response)
        return str(response)

    def rpc_hello(self):
        return 'world!'

    def rpc_add(self, a, b):
        return int(a) + int(b)
    
def form():
    return """
    <form action='recv'>
    Amount to convert: <input type='number' name='amount' size'10'>
    Measurement used: <select name='measurement'>
    <option value='oz'>Ounces</option>
    <option value='gal'>Gallon</option>
    <option value='lt'>Liter</option></select>
    <input type='submit'>
    </form>
    """
