#! /usr/bin/env python
from wsgiref.simple_server import make_server
import urlparse
import simplejson
import db, recipes
from db import Party
from Cookie import SimpleCookie
import jinja2
import uuid

dispatch = {
    '/' : 'index',
    '/login_1' : 'login1',
    '/login1_process' : 'login1_process',
    '/logout' : 'logout',
    '/status' : 'status',
    '/recipes' : 'recipes',
    '/inventory' : 'inventory',
    '/liquor' : 'liquor',
    '/party_list' : 'party_list',
    '/party_info' : 'party_info',
    '/party_join' : 'party_join',
    '/party_submit' : 'party_submit',
    '/party_make' : 'party_make',
    '/party_make_submit' : 'party_make_submit',
    '/form' : 'form',
    '/recv' : 'recv',
    '/rpc'  : 'dispatch_rpc'
}

html_headers = [('Content-Type', 'text/html')]

usernames = {}

loader = jinja2.FileSystemLoader('./jinja2/templates')
env = jinja2.Environment(loader=loader)

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
        <html><head><title>Home - Drinkz - Alex Lockwood</title>
        <style type="text/css">
        h1 {color:red;}
        p {color:black;}
        </style></head><body>

        <h1>Table of Contents</h1><p>
        <a href='login_1'>Login</a><br>
        <a href='status'>Status</a><br>
        <a href='logout'>Logout</a><br>
        <a href='recipes'>List of Recipes</a><br>
        <a href='inventory'>Inventory</a><br>
        <a href='liquor'>Liquor Types</a><br>
        <a href='party_list'>List of parties</a><br>
        <a href='form'>Volume Converter</a><br></p></body></html>
        """

        start_response('200 OK', list(html_headers))
        return [data]

    def login1(self, environ, start_response):
        start_response('200 OK', list(html_headers))
        
        title = 'login'
        template = env.get_template('login1.html')
        return str(template.render(locals()))

    def login1_process(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        name = results['name'][0]
        content_type = 'text/html'

        # authentication would go here -- is this a valid username/password,
        # for example?

        k = str(uuid.uuid4())
        usernames[k] = name

        headers = list(html_headers)
        headers.append(('Location', '/status'))
        headers.append(('Set-Cookie', 'name1=%s' % k))

        start_response('302 Found', headers)
        return ["Redirect to /status..."]

    def logout(self, environ, start_response):
        if 'HTTP_COOKIE' in environ:
            c = SimpleCookie(environ.get('HTTP_COOKIE', ''))
            if 'name1' in c:
                key = c.get('name1').value
                name1_key = key

                if key in usernames:
                    del usernames[key]
                    print 'DELETING'

        pair = ('Set-Cookie',
                'name1=deleted; Expires=Thu, 01-Jan-1970 00:00:01 GMT;')
        headers = list(html_headers)
        headers.append(('Location', '/status'))
        headers.append(pair)

        start_response('302 Found', headers)
        return ["Redirect to /status..."]

    def status(self, environ, start_response):
        start_response('200 OK', list(html_headers))

        name1 = ''
        name1_key = '*empty*'
        if 'HTTP_COOKIE' in environ:
            c = SimpleCookie(environ.get('HTTP_COOKIE', ''))
            if 'name1' in c:
                key = c.get('name1').value
                name1 = usernames.get(key, '')
                name1_key = key
                
        title = 'login status'
        template = env.get_template('status.html')
        return str(template.render(locals()))
        
    def recipes(self, environ, start_response):
        content_type = 'text/html'
        data = """\
        <html><head><title>Recipes - Drinkz - Alex Lockwood</title>
        <style type="text/css">
        h1 {color:red;}
        p {color:black;}
        </style></head><body>
        <h1>Recipe List</h1>
        <a href='/'>Return to Index</a><p>
        """

        for recipe in db.get_all_recipes():
            data += "<li> %s: " % recipe.name
            if not recipe.need_ingredients():
                data += "AVAILABLE"
            else:
                data += "NEED "
                for (l, a) in recipe.need_ingredients():
                    data += "%s - %sml, " % (l, a)

        data += "</p></body></html>"
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
        <html><head><title>Inventory - Drinkz - Alex Lockwood</title>
        <style type="text/css">
        h1 {color:red;}
        p {color:black;}
        </style></head><body>
        <h1>Inventory List</h1>
        <a href='/'>Return to Index</a><p>
        """

        for (m, f) in db._inventory_db:
            data += "<li> %s - %s - %s" % (m, f, db._inventory_db[(m, f)])

        data += "</p></body></html>"        
        start_response('200 OK', list(html_headers))
        return [data]

    def liquor(self, environ, start_response):
        content_type = 'text/html'
        data = """\
        <html><head><title>Liquors - Drinkz - Alex Lockwood</title>
        <style type="text/css">
        h1 {color:red;}
        p {color:black;}
        </style></head><body>
        <h1>Liquor List</h1>
        <a href='/'>Return to Index</a><p>
        """

        for (m, f, g) in db._bottle_types_db:
            data += "<li> %s - %s - %s" % (m, f, g)

        data += "</ul></p></body></html>"
        start_response('200 OK', list(html_headers))
        return [data]

    def party_list(self, environ, start_response):
        content_type = 'text/html'
        data = """\
        <html><head><title>Party List - Drinkz - Alex Lockwood</title>
        <style type="text/css">
        h1 {color:red;}
        p {color:black;}
        </style></head><body>
        <h1>Party List</h1>
        <a href='/'>Return to Index</a><p>
        <h3>Current Parties:</h3>
        """

        for p in db._parties:
            data += "<b>%s</b><br>Hosted by: %s<br><br>" % (p.title, p.user)

        data += "<br><form action='party_info'>"
        data += "Read about a party: <select name='party_choice'>"
        for p in db._parties:
            data += "<option value='%s'>%s</option>" % (p.user, p.title)
        data += "</select><input type='submit' value='Check it out!'></form><br>"

        data += "<form action='party_make'><input type='submit' value='CREATE YOUR OWN PARTY'></form></p></body></html>"
        start_response('200 OK', list(html_headers))
        return [data]

    def party_info(self, environ, start_response):
        content_type = 'text/html'

        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        p = db.get_party(results['party_choice'][0])

        data = """\
        <html><head><title>Party Info - Drinkz - Alex Lockwood</title>
        <style type="text/css">
        h1 {color:red;}
        p {color:black;}
        </style></head><body>
        <h1>Party Info</h1>
        <a href='/'>Return to Index</a><p>
        """

        data += "<h3><b><u>%s</u></b></h3>Host: %s<br>Date: %s<br>Time: %s<br>Address: %s<br><br>RECIPES REQUESTED:<br>" % (p.title, p.user, p.date, p.time, p.address)

        for r in p.recipes:
            data += "<li> %s<br>" % (r)
            for (n, a) in p.recipes[r].ingredients:
                data += "- %s : %s<br>" % (n, a)

        data += "<br>LIQUORS PROVIDED:<br>"
        for l in p.liquors:
            data += "<li> %s, %s: %s ml<br>" % (l[0], l[1], p.liquors[l])

        data += "<br>USERS ATTENDING:<br>"
        for u in p.attending:
            data += "<li> %s" % u

        data += "<br><br><form action='party_join'><input type='submit' value='JOIN PARTY!'><input name='party_choice' type='hidden' value='%s'></form></p></body></html>" % results['party_choice'][0]
        start_response('200 OK', list(html_headers))
        return [data]

    def party_join(self, environ, start_response):
        content_type = 'text/html'

        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        p = db.get_party(results['party_choice'][0])

        data = """\
        <html><head><title>Join Party - Drinkz - Alex Lockwood</title>
        <style type="text/css">
        h1 {color:red;}
        p {color:black;}
        </style></head><body>
        <h1>Join Party</h1>
        <a href='/'>Return to Index</a><p>
        """

        data += "<h3><b><u>%s</u></b></h3>Please bring 1 - 3 liquors, defined as Manufacturer/Liquor/Amount(ml):<br>" % p.title
        data += "<form action='party_submit'><input type='text' name='m1'><input type='text' name='l1'><input type='number' name='a1' min='1' max='5000'><br>"
        data += "<input type='text' name='m2'><input type='text' name='l2'><input type='number' name='a2' min='1' max='5000'><br>"
        data += "<input type='text' name='m3'><input type='text' name='l3'><input type='number' name='a3' min='1' max='5000'><br>"
        data += "<input type='submit'><input name='party_choice' type='hidden' value='%s'></form></p></body></html>" % results['party_choice'][0]

        start_response('200 OK', list(html_headers))
        return [data]

    def party_submit(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)
        content_type = 'text/html'

        p = db.get_party(results['party_choice'][0])
        
        m1=m2=m3=l1=l2=l3=a1=a2=a3=''
        
        if results.has_key('m1'):
            m1 = results['m1'][0]
        if results.has_key('m2'):
            m2 = results['m2'][0]
        if results.has_key('m3'):
            m3 = results['m3'][0]
        if results.has_key('l1'):
            l1 = results['l1'][0]
        if results.has_key('l2'):
            l2 = results['l2'][0]
        if results.has_key('l3'):
            l3 = results['l3'][0]
        if results.has_key('a1'):
            a1 = results['a1'][0]
        if results.has_key('a2'):
            a2 = results['a2'][0]
        if results.has_key('a3'):
            a3 = results['a3'][0]

        liquors = dict()
        if m1 != '' and l1 != '' and a1 != '':
            liquors[(m1,l1)] = a1
        if m2 != '' and l2 != '' and a2 != '':
            liquors[(m2,l2)] = a2
        if m3 != '' and l2 != '' and a3 != '':
            liquors[(m3,l3)] = a3
        print liquors
        p.add_liquor(liquors)

        username = ''
        if 'HTTP_COOKIE' in environ:
            c = SimpleCookie(environ.get('HTTP_COOKIE', ''))
            if 'name1' in c:
                key = c.get('name1').value
                name1_key = key

                if key in usernames:
                    username = str(usernames[key])
        if username == '':
            username = "Anonymous"

        p.add_attending(username)

        data = """\
        <html><head><title>Party Joined! - Drinkz - Alex Lockwood</title>
        <style type="text/css">
        h1 {color:red;}
        p {color:black;}
        </style></head><body>
        <h1>Party Joined!</h1>
        <a href='/'>Return to Index</a><p>
        """

        start_response('200 OK', list(html_headers))
        return [data]

    def party_make(self, environ, start_response):
        content_type = 'text/html'

        username = ''
        if 'HTTP_COOKIE' in environ:
            c = SimpleCookie(environ.get('HTTP_COOKIE', ''))
            if 'name1' in c:
                key = c.get('name1').value
                name1_key = key

                if key in usernames:
                    username = str(usernames[key])
        if username == '':
            username = "Anonymous"

        data = """\
        <html><head><title>Create a Party - Drinkz - Alex Lockwood</title>
        <style type="text/css">
        h1 {color:red;}
        p {color:black;}
        </style></head><body>
        <h1>Create a Party!</h1>
        <a href='/'>Return to Index</a><p>
        """

        data += "<form action='party_make_submit'>Please input the following information:<br>"
        data += "Party title: <input type='text' name='title'><br>Date: <input type='text' name='date'><br>Time: <input type='text' name='time'><br>Address: <input type='text' name='address'><br>"

        data += "Enter up to three liquors you're bringing:<br>"
        data += "Brand: <input type='text' name='m1'>Liquor: <input type='text' name='l1'>Amount (ml): <input type=number name='a1' min='0' max='5000'>"
        data += "Brand: <input type='text' name='m2'>Liquor: <input type='text' name='l2'>Amount (ml): <input type=number name='a2' min='0' max='5000'>"
        data += "Brand: <input type='text' name='m3'>Liquor: <input type='text' name='l3'>Amount (ml): <input type=number name='a3' min='0' max='5000'>"
        data += "<input type='submit' value='CREATE PARTY!'><input name='user' type='hidden' value='%s'></form></p></body></html>"% username
        start_response('200 OK', list(html_headers))
        return [data]

    def party_make_submit(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)
        content_type = 'text/html'

        user = results['user'][0]

        m1=m2=m3=l1=l2=l3=a1=a2=a3=title=date=time=address=''

        if results.has_key('m1'):
            m1 = results['m1'][0]
        if results.has_key('m2'):
            m2 = results['m2'][0]
        if results.has_key('m3'):
            m3 = results['m3'][0]
        if results.has_key('l1'):
            l1 = results['l1'][0]
        if results.has_key('l2'):
            l2 = results['l2'][0]
        if results.has_key('l3'):
            l3 = results['l3'][0]
        if results.has_key('a1'):
            a1 = results['a1'][0]
        if results.has_key('a2'):
            a2 = results['a2'][0]
        if results.has_key('a3'):
            a3 = results['a3'][0]
        if not results.has_key('title'):
            title = "Party"
        else:
            title = results['title'][0]
        if not results.has_key('date'):
            date = "Tonight!"
        else:
            date = results['date'][0]
        if not results.has_key('time'):
            time = "11:00PM"
        else:
            time = results['time'][0]
        if not results.has_key('address'):
            address = "Text for address"
        else:
            address = results['address'][0]

        liquors = dict()
        if m1 != '' and l1 != '' and a1 != '':
            liquors[(m1,l1)] = a1
        if m2 != '' and l2 != '' and a2 != '':
            liquors[(m2,l2)] = a2
        if m3 != '' and l2 != '' and a3 != '':
            liquors[(m3,l3)] = a3

        newParty = Party(user, title, date, time, address, dict(), liquors)
        db.add_party(newParty)
        
        data = """\
        <html><head><title>Party Created! - Drinkz - Alex Lockwood</title>
        <style type="text/css">
        h1 {color:red;}
        p {color:black;}
        </style></head><body>
        <h1>Party Created!</h1>
        <a href='/'>Return to Index</a><p>
        """

        start_response('200 OK', list(html_headers))
        return [data]

    def form(self, environ, start_response):
        data = form()

        start_response('200 OK', list(html_headers))
        return [data]
   
    def recv(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        origAmount = 0
        if results.has_key('amount'):
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
        data = """\
        <html><head><title>Liquors - Drinkz - Alex Lockwood</title>
        <style type="text/css">
        h1 {color:red;}
        p {color:black;}
        </style></head><body>
        <h1>mL Converter</h1>
        """

        data += "%s %s = %s ml<br><br> <a href='/'>Return to Index</a>" % (origAmount, measurement, amount)

        data += "</ul></p></body></html>"
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

    def rpc_convert_units_to_ml(self, amount):
        return db.convertToMl(amount)

    def rpc_get_recipe_names(self):
        recipe_list = []
        for r in db.get_all_recipes():
            recipe_list.append(r.name)
        return recipe_list

    def rpc_get_liquor_inventory(self):
        liquor_list = []
        for (m, l) in db.get_liquor_inventory():
            liquor_list.append((m, l))
        return liquor_list

def form():
    return """
    <html><head><title>mL Converter - Drinkz - Alex Lockwood</title>
    <style type="text/css">
    h1 {color:red;}
    p {color:black;}
    </style></head><body>
    <h1>mL Converter</h1>
    <a href='/'>Return to Index</a><p>
    <form action='recv'>
    Amount to convert: <input type='number' name='amount' min="0" size'10'>
    Measurement used: <select name='measurement'>
    <option value='oz'>Ounces</option>
    <option value='gal'>Gallon</option>
    <option value='lt'>Liter</option></select>
    <input type='submit'>
    </form>
    """
