from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import json
import events
import threading
from irc import IrcConnection

HOST, PORT = '', 8888

irc = None

# handle POST events from github server
# We should also make sure to ignore requests from the IRC, which can clutter
# the output with errors
class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pass
    def do_CONNECT(self):
        pass
    def do_POST(self):
        content_type = self.headers.getheader('content-type', 'bad content')
        if not content_type == 'application/json':
            return

        content_len = int(self.headers.getheader('content-length', 0))

        event_type = self.headers.getheader('x-github-event', 'ping')
        data = self.rfile.read(content_len)

        self.send_response(200)
        self.end_headers()
        self.wfile.write("OK")
        self.finish();

        events.handle_event(irc, event_type, json.loads(data))
        return

# Just run IRC connection event loop
def worker():
    irc.loop()

irc = IrcConnection(server='chat.freenode.net', channel='#wfbottest', nick='wftestbot', port=6667)
t = threading.Thread(target=worker)
t.start()

# Run Github webhook handling server
try:
    server = HTTPServer((HOST, PORT), MyHandler)
    server.serve_forever()
except KeyboardInterrupt:
    print "Exiting"
    server.socket.close()
    irc.stop_loop()
