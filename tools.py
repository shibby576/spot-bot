from typing import Optional, Type
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
import requests
from flask import session

#get headers
def get_auth_header():
    header = session.get('auth_header')
    return header

#Skip song
class skipSong(BaseTool):
    name = "Skip"
    description = "useful for when you need to skip the current song on spotify. Do not use this tool to check if the right song is playing"

    def _run(self,song):
        """Use the tool."""
        headers = get_auth_header()
        url = 'https://api.spotify.com/v1/me/player/next'
        response = requests.post(url, headers=headers)
        return response
    def _arun(self,song):
        raise NotImplementedError("This tool does not support async")

#Pause song
class pauseSong(BaseTool):
    name = "Pause"
    description = "useful for when you need to pause the current song on spotify"

    def _run(self,song):
        """Use the tool."""
        headers = get_auth_header()
        url = 'https://api.spotify.com/v1/me/player/pause'
        response = requests.put(url, headers=headers)
        return response
    def _arun(self,song):
        raise NotImplementedError("This tool does not support async")

#Resume song
class resumeSong(BaseTool):
    name = "Resume"
    description = "useful for when you need to resume the current song on spotify"

    def _run(self,song):
        """Use the tool."""
        headers = get_auth_header()
        url = 'https://api.spotify.com/v1/me/player/play'
        response = requests.put(url, headers=headers)
        return response
    def _arun(self,song):
        raise NotImplementedError("This tool does not support async")

#search for a song and return the context uri
from pydantic import BaseModel, Field
class SearchSchema(BaseModel):
    query: str = Field(description="should be a search query that includes an artist and or track name")


class searchSong(BaseTool):
    name = "Search"
    description = "useful for when you need to search for a song or artist to play on spotify. This returns the uri that can be used to play the song"
    args_schema: Type[SearchSchema] = SearchSchema
    
    def _run(self,query):
        """Use the tool."""
        headers = get_auth_header()
        url = 'https://api.spotify.com/v1/search?q={search}&type=artist%2Ctrack&market=US&limit=5&offset=0'
        response = requests.get(url.format(search=query), headers=headers)
        data = response.json()
        first_track_uri = data['tracks']['items'][0]['uri']
        return first_track_uri
    def _arun(self,query):
        raise NotImplementedError("This tool does not support async")

#Play a song based on search

class playSongSchema(BaseModel):
    track: str = Field(description="should be a string that looks like spotify:track:1kKYjjfNYxE0YYgLa7vgVY")


class playSong(BaseTool):
    name = "Play"
    description = "useful for when you need to play a song on spotify based on the track uri. You need to Search for the track URI with the Search tool first"
    args_schema: Type[playSongSchema] = playSongSchema
    
    def _run(self,track):
        """Use the tool."""
        headers = get_auth_header()
        data = {"uris": [track]}
        url = 'https://api.spotify.com/v1/me/player/play'
        response = requests.put(url,json=data, headers=headers)
        
        return response
    def _arun(self,data):
        raise NotImplementedError("This tool does not support async")

#Check the current song playing

class checkSong(BaseTool):
    name = "Check"
    description = "useful for when you need to find out if there is a song playing on spotify or if you need to get the uri of the current song playing. It returns the URI of the current song playing."

    def _run(self,song):
        """Use the tool."""
        headers = get_auth_header()
        url = 'https://api.spotify.com/v1/me/player'
        response = requests.get(url, headers=headers)
        response_data = response.json()
        # Retrieve the URI value from the response
        track_uri = response_data['item']['uri']
        return track_uri
    def _arun(self,song):
        raise NotImplementedError("This tool does not support async")

#Play a song similar to the current one

class similarSongSchema(BaseModel):
    track: str = Field(description="should be a uri string that looks like spotify:track:1kKYjjfNYxE0YYgLa7vgVY")

class findSimilarSong(BaseTool):
    name = "Find similar song"
    description = "useful for when you need to find a song that is similar to the song currently playing on spotify. It returns the URI of a similar song which can be used to play the song."
    args_schema: Type[similarSongSchema] = similarSongSchema
        
    def _run(self,track):
        """Use the tool."""
        headers = get_auth_header()
        url = 'https://api.spotify.com/v1/recommendations?limit=10&market=US&seed_tracks={track}'
        response = requests.get(url.format(track=track.split(":")[2]), headers=headers)
        response_data = response.json()
        # Retrieve the URI value from the response
        track_uri = response_data['tracks'][0]['uri']
        return track_uri
    def _arun(self,track):
        raise NotImplementedError("This tool does not support async")

# Add song to queue

class queueSongSchema(BaseModel):
    track: str = Field(description="should be a uri string that looks like spotify:track:1kKYjjfNYxE0YYgLa7vgVY")

class addToQueue(BaseTool):
    name = "Add song to queue"
    description = "useful for when you need to add a song to the user's queue on spotify. It takes a track URI and adds it to the queue."
    args_schema: Type[queueSongSchema] = queueSongSchema
        
    def _run(self,track):
        """Use the tool."""
        headers = get_auth_header()
        url = 'https://api.spotify.com/v1/me/player/queue?uri={track}'
        response = requests.post(url.format(track=track), headers=headers)
        return response
    def _arun(self,track):
        raise NotImplementedError("This tool does not support async")
    
def createTools():
    tools = [skipSong(),pauseSong(),resumeSong(),searchSong(),playSong(),checkSong(),findSimilarSong(),addToQueue()]
    return tools