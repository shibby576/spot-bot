import os
from flask import Flask, redirect, render_template, request, url_for,jsonify,session
import requests
import base64
from tools import createTools
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
import tools
from dotenv import load_dotenv




load_dotenv()

app = Flask(__name__)

client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')
app.secret_key = os.getenv('app.secret_key')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

#redirect_uri = 'http://localhost:5000/callback'
redirect_uri = 'https://www.spot-bot.xyz/callback'
authorization_base_url = 'https://accounts.spotify.com/authorize'
token_url = 'https://accounts.spotify.com/api/token'
scopes=['app-remote-control', 'playlist-modify-private', 'playlist-modify-public', 'playlist-read-collaborative', 'playlist-read-private', 'streaming', 'ugc-image-upload', 'user-follow-modify', 'user-follow-read', 'user-library-modify', 'user-library-read', 'user-modify-playback-state', 'user-read-currently-playing', 'user-read-email', 'user-read-playback-position', 'user-read-playback-state', 'user-read-private', 'user-read-recently-played', 'user-top-read']
scope=','.join(scopes)

tools = createTools()
#import openai and set llm

llm = ChatOpenAI(temperature=0)
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,max_iterations=6,handle_parsing_errors=True, verbose=True,max_execution_time=10,return_intermediate_steps=True)


@app.route('/')
def home():
    return render_template('index.html', client_id=client_id, redirect_uri=redirect_uri,scope=scope)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    client_credentials = base64.urlsafe_b64encode(f"{client_id}:{client_secret}".encode()).decode()
    auth_header = {'Authorization': f"Basic {client_credentials}"}


    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
    }
    
    response = requests.post(token_url, headers=auth_header, data=data)
    tokens = response.json()

    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')

    #save auth header as session variable
    session['auth_header'] = {'Authorization': f'Bearer {access_token}'}

    if access_token and refresh_token:
        # Redirect to the index page with a "success" URL parameter
        return redirect(url_for('home') + '?auth_success=1')
    else:
        # Redirect to the index page with an "error" URL parameter
        return redirect(url_for('home') + '?auth_error=1')

@app.route('/submit', methods=['POST'])
def submit():
    input_text = request.get_json().get('text', '')
    if not input_text:
        return jsonify(error='Invalid input')
    
    result = agent(input_text)
   # Serialize the agent_response object
    serialized_agent_response = serialize_agent_response(result)
    print(serialized_agent_response)

    return jsonify(result=serialized_agent_response)



from requests.models import Response  

def serialize_agent_response(agent_response):
    new_intermediate_steps = []

    for step in agent_response['intermediate_steps']:
        serialized_step = []

        for item in step:
            if isinstance(item, Response):
                serialized_item = {
                    'status_code': item.status_code,
                    'reason': item.reason,
                    'text': item.text  
                }
            else:
                serialized_item = item

            serialized_step.append(serialized_item)

        new_intermediate_steps.append(tuple(serialized_step))

    serialized_agent_response = agent_response.copy()
    serialized_agent_response['intermediate_steps'] = new_intermediate_steps

    return serialized_agent_response





if __name__ == '__main__':
    app.run(debug=True)