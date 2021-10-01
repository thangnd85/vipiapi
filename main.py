from flask import Flask, request, jsonify, render_template
from flask_restful import Resource, Api
from flask_cors import CORS
import urllib.request, random, os, pathlib, sys, time, requests, json, re, datetime, urllib, sys, subprocess
from os import listdir, path
from urllib.request import urlretrieve
from fuzzywuzzy import fuzz
from itertools import combinations
from youtubesearchpython import *
from bs4 import BeautifulSoup
import xmltodict
app = Flask(__name__)
api = Api(app)
CORS(app)
try:
    import pafy
except:
    os.system('pip install git+https://github.com/mps-youtube/pafy')
    import pafy

def youtube_stream_link(data):
    lists = {'id':[],'name':[],'audio':[],'video':[]}
    for video in CustomSearch(data, VideoSortOrder.viewCount, language = 'vi', region = 'VN',limit=5).result()['result']:
        lists['id'].append(video['id'])
        lists['name'].append(video['title'])
        video_url="https://www.youtube.com/watch?v="+video['id']
        video = pafy.new(video_url)
        best_video = video.getbest()
        best_audio = video.getbestaudio()
        try:
            audio_streaming_link = best_audio.url
        except:
            audio_streaming_link = best_video.url
        video_streaming_link = best_video.url
        lists['audio'].append(audio_streaming_link)
        lists['video'].append(video_streaming_link)
    return lists

def zingmp3(data):
    result=None
    if 'của' in data.lower():
        song = re.split(r"\ của", data.lower())[0]
        try:
            artist = re.split(r"\ của", data.lower())[1]
        except:
            artist = ''
    else: 
        song = data
        artist=''
    try:
        resp = requests.get('http://ac.mp3.zing.vn/complete?type=artist,song,key,code&num=500&query='+urllib.parse.quote(song+" "+artist))
        resultJson = json.dumps(resp.json())
        obj = json.loads(resultJson)
        song_id=[]
        if len(obj['data']) > 0:
            songs = obj['data'][0]['song']
            for i in range (0,len(songs)):
                if str(songs[i]['name']).lower()==str(song).lower() and str(songs[i]['artist']).lower()==str(artist).lower():
                    song_id.append(songs[i]['id'])      
                elif str(songs[i]['name']).lower()==str(song).lower():
                    song_id.append(songs[i]['id'])
                else:
                    song_id.append(songs[i]['id'])
        else:
            pass
        songID =  random.choice(song_id)
        songUrl= "https://mp3.zing.vn/bai-hat/"+songID+".html"
        resp = requests.get(songUrl)
        key = re.findall('o&key=([a-zA-Z0-9]{20,35})', resp.text)
        songApiUrl = "https://mp3.zing.vn/xhr/media/get-source?type=audio&key="+key[0]
        resp = requests.get(songApiUrl)
        resultJson = json.dumps(resp.json())
        obj = json.loads(resultJson)
        mp3Source = "https:"+obj["data"]["source"]["128"]
        realURLdata = requests.get(mp3Source,allow_redirects=False)
        realURL = realURLdata.headers['Location']
        return realURL
    except (IndexError, ValueError):
        return None

def nhaccuatui(query):
    print ('Tìm bài hát trên NCT: '+query)    
    try:
        response = requests.get("https://www.nhaccuatui.com/tim-kiem?q="+query)
        soup = BeautifulSoup(response.content, "html.parser")
        if soup.find_all("div", {"class": "sn_box_search_suggest"}):
            titles = soup.findAll('div', class_='sn_box_search_suggest')
            link = soup.findAll('h3', class_='sn_name_album_search')
            linkbaihat = (link[0].find('a')).get('href')
            
        else:
            titles = soup.findAll('li', class_='sn_search_single_song')
            linkbaihat = (titles[0].find('a')).get('href')
        
        video = 0
        baihat = requests.get(linkbaihat)
        soup1 = BeautifulSoup(baihat.content, "html.parser").decode('utf-8')
        key = re.findall('&key1=([a-zA-Z0-9]{0,35})', soup1)
        if(not key):
            video = 1
            key = re.findall('key3=([a-zA-Z0-9]{0,35})&', soup1)                
        if video == 1:
            response = requests.get("https://www.nhaccuatui.com/flash/xml?key3="+key[0]+"&html5=true&listKey=")
            data = xmltodict.parse(response.content)
            return (data['tracklist']['track']['location']), (data['tracklist']['track']['title']),(data['tracklist']['track']['creator'])
        else:
            response = requests.get("https://www.nhaccuatui.com/flash/xml?html5=true&key1="+key[0])
            data = xmltodict.parse(response.content)
            return (data['tracklist']['track']['location']), (data['tracklist']['track']['title']),(data['tracklist']['track']['creator'])
            pass
    except:
        return None,None,None
class status (Resource):
    def get(self):
        try:
            return {'data': 'Api is Running'}
        except:
            return {'data': 'An Error Occurred during fetching Api'}

class search(Resource):
    def get(self):
        data = request.args.get('song', default = 'Tình đơn phương remix')
        link = youtube_stream_link(data)
        return {'status': link}
class nct(Resource):
    def get(self):
        data = request.args.get('song', default = 'Tình đơn phương remix')
        link = nhaccuatui(data)
        return {'status': link}
class zing(Resource):
    def get(self):
        data = request.args.get('song', default = 'Tình đơn phương remix')
        link = zingmp3(data)
        return {'status': link}
class Sum(Resource):
    def get(self, a, b):
        return jsonify({'data': a+b})


api.add_resource(status, '/')
api.add_resource(search, '/search')
api.add_resource(nct, '/nct')
api.add_resource(zing, '/zing')
api.add_resource(Sum, '/add/<int:a>,<int:b>')


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)
