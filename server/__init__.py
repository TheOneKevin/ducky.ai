import flask
from .session import *
from .notify import get_announcer
import lib as lp

# Warm up the OpenAI API
lp.resolve_provider('openai')
# Fetch the flows initially
reload_flows()

app = flask.Flask(__name__)

def current_session() -> ChatSessionWrapper | None:
   try:
      sessionid = flask.request.cookies.get('session')
      assert sessionid is not None
      return get_session(sessionid)
   except:
      return None

@app.route('/')
def main():
   context = {
      'flows': get_flows()
   }
   return flask.render_template('index.html', **context)

@app.route('/api/listen', methods=['GET'])
def api_listen():
   def stream():
      messages = get_announcer().listen()
      while True:
         msg = messages.get()
         yield msg
   return flask.Response(stream(), mimetype='text/event-stream')

@app.route('/api/ping', methods=['POST'])
def api_ping():
   get_announcer().announce(data='pong', event='ping')
   return {}, 200

@app.route('/api/session/send', methods=['POST'])
def api_session_send():
   data = flask.request.get_json()
   # Check if the request contains a message
   if 'message' not in data:
      return {'error': 'No message provided'}, 400
   # Check if the message is empty
   if data['message'] == '':
      return {'error': 'Message is empty'}, 400
   # Grab the current session
   session = current_session()
   if not session:
      return {'error': 'Invalid session cookie'}, 400
   # Send the message
   error = session.send_message(data['message'])
   if error:
      return {'error': error}, 400
   return {'status': 'OK'}, 200

@app.route('/api/session/model', methods=['GET'])
def api_session_model():
   # Check for the session cookie, if it doesn't exist, create it
   exists = 'session' in flask.request.cookies
   exists = exists and session_exists(flask.request.cookies.get('session'))
   if not exists:
      print('Creating new session')
      session = new_session()
      resp = flask.make_response(session.serialize())
      resp.set_cookie('session', session.id)
      return resp, 200
   else:
      sessionid = flask.request.cookies.get('session')
      try:
         assert sessionid is not None
         session = get_session(sessionid)
      except:
         return {'error': 'Invalid session cookie'}, 400
      return session.serialize(), 200

@app.route('/api/session/new', methods=['POST'])
def api_session_new():
   # Reset the session cookie
   resp = flask.make_response({})
   resp.delete_cookie('session')
   return resp, 200

@app.route('/api/session/flow/<flowid>', methods=['POST'])
def api_session_flow(flowid):
   # Grab the current session
   session = current_session()
   if not session:
      return {'error': 'Invalid session cookie'}, 400
   # Check if the flow exists and grab it
   flow = [ f for f in get_flows() if f.id == flowid ]
   flow = flow[0] if len(flow) == 1 else None
   if not flow:
      return {'error': 'Invalid flow ID'}, 400
   # Set the session's flow
   session.selected_flow = flow
   return {'status': 'OK'}, 200

@app.route('/api/flows/reload', methods=['POST'])
def api_flows_reload():
   reload_flows()
   return {'status': 'OK'}, 200
