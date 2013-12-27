import json
import random
from datetime import datetime

from bson import json_util, ObjectId
import motor
import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado import gen

# class Application(tornado.web.Application):
#     def __init__(self):
#         handlers = [
#             (r"/api/channel", ServiceHandler)
#         ]
#         super(Application, self).__init__(handlers)
#         self.db = tornado.database.Connection(
#             host='localhost', database='project', user='root', password=''
#         )

class ChannelHandler(tornado.web.RequestHandler):
    def get_js_code(self, code, inject):
        # return code
        code = json.dumps(code)
        code = code.replace('<script', '\x3Cscript')
        code = code.replace('</script>', '\x3C/script>')

        js_code = "(function(){document.write(%s)})();" % code
        # js_code = "(function(){var inject='%s'; if (document.getElementById(inject) != null) document.getElementById(inject).innerHTML = %s; console.log(document.getElementById(inject).childNodes[0].innerHTML);eval(document.getElementById(inject).childNodes[0].innerHTML);})();" % (inject, code)
        return js_code

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self, id_):
        db = self.settings['db']
        inject = self.get_argument('inject', None)
        # cursor = db.channels.find().sort([('_id', -1)])

        self.set_header("Content-Type", "application/javascript; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")

        # obj = yield motor.Op(db.channels.find_one, ObjectId(id_))
        # self.write(json.dumps(obj, default=json_util.default))


        # self.write('[')
        # i = 0
        # while (yield cursor.fetch_next):
        #     channel = cursor.next_object()
        #     if i != 0:
        #         self.write(', ')
        #     self.write(json.dumps(channel, default=json_util.default))
        #     i += 1
        # self.write(']')

        cursor = db.codes.find({'channel_id': ObjectId(id_)})
        codes = yield motor.Op(cursor.to_list, 20)
        code = random.choice(codes)
        code_code = code['code']
        js_code = self.get_js_code(code_code, inject)
        self.write(js_code)
        # self.write(json.dumps(channels, default=json_util.default))

        self.finish()

        db.statistics.insert({
            'channel_id': ObjectId(id_),
            'code_id': code['_id'],
            # 'code_name': code['name'],
            'remote_ip': self.request.remote_ip,
            'user_agent': self.request.headers['User-Agent'],
            'time': datetime.now()
        })


application = tornado.web.Application([
    (r'/channel/([^/]*)/?', ChannelHandler)
])


if __name__ == "__main__":
    server = tornado.httpserver.HTTPServer(application)
    server.bind(8888)

    # start(0) starts a subprocess for each CPU core
    server.start(0)

    # If you want to use the Tornado HTTP server's start() method to fork
    # multiple subprocesses, you must create the client object after calling
    # start(), since a client created before forking isn't valid after
    client = motor.MotorClient('mongodb://localhost:27017').open_sync()
    db = client['ad_server_01']

    # Delayed initialization of settings
    application.settings['db'] = db
    tornado.ioloop.IOLoop.instance().start()