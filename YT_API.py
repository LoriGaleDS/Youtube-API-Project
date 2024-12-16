#!/usr/bin/env python
# coding: utf-8

# In[2]:


from googleapiclient.discovery import build
import pandas as pd
from IPython.display import JSON
from dateutil import parser
import isodate
import seaborn as sns 
import matplotlib.pyplot as  plt


# In[3]:


api_key_project1 = "AIzaSyC4GI7hURrd-kSVurCxNy1iO8BTyP1IH6U"
id_channel = ["UCN7x37T8InfV3DINfYKvOQQ"]


# In[4]:


api_service_name = "youtube"
api_version = "v3"
youtube = build(api_service_name, api_version, developerKey = api_key_project1)


# In[5]:


request = youtube.channels().list(
        part = "snippet,contentDetails,statistics",
        id= ','.join(id_channel)
        )
response = request.execute()

JSON(response)


# In[6]:


def get_channel_stats(youtube,channel_ids):
    all_data = []

    request = youtube.channels().list(
        part = "snippet,contentDetails,statistics",
        id= ','.join(id_channel)
        )
    response = request.execute()

    #loop through items (if you need more than 1 channel)
    for item in response["items"]:
        data = {"channelName": item["snippet"]["title"],
                "subscribers": item["statistics"]["subscriberCount"],
                "views": item["statistics"]["viewCount"],
                "totalVideos": item["statistics"]["videoCount"],
                "playlistId": item["contentDetails"]["relatedPlaylists"]["uploads"]
               }
        all_data.append(data)
    return(pd.DataFrame(all_data))


# In[7]:


channel_stats = get_channel_stats(youtube,id_channel)
channel_stats


# In[8]:


playlistId = "UUN7x37T8InfV3DINfYKvOQQ"


# In[9]:


def get_videos_id(youtube,playlistId):

    videosIdList = []
    
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlistId,
        maxResults = 50
        )
    response = request.execute()

    for item in response["items"]:
        videoId = item["contentDetails"]["videoId"]
        videosIdList.append(videoId)
    next_page_token = response.get("nextPageToken")
    while next_page_token is not None:
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlistId,
            maxResults = 50,
            pageToken = next_page_token
            )
        response = request.execute()

        for item in response["items"]:
            videoId = item["contentDetails"]["videoId"]
            videosIdList.append(videoId)
        next_page_token = response.get("nextPageToken")
    return(videosIdList)


# In[10]:


videosIDs = get_videos_id(youtube,playlistId)
len(videosIDs)


# In[26]:


def get_video_details(youtube, video_ids):
    all_video_info = []
    
    request = youtube.videos().list(
        part="snippet, contentDetails,statistics",
        id = videosIDs[0:50]
        )
    response = request.execute()
    for item in response["items"]:
        stats_to_keep = {"snippet":["channelTitle","title","description","tags","publishedAt"],
                         "statistics":["viewCount","likeCount","favouriteCount","commentCount"],
                         "contentDetails":["duration","caption"]
                        }
        video_info = {}
        video_info["video_id"] = item["id"]
        for k in stats_to_keep.keys():
            for v in stats_to_keep[k]:
                try:
                    video_info[v] = item[k][v]
                except:
                    video_info[v] = None
                
                
    
        all_video_info.append(video_info)
    return pd.DataFrame(all_video_info)
        


# In[27]:


df_video = get_video_details(youtube, videosIDs)
df_video


# In[28]:


df_video.isnull().any()


# In[29]:


df_video.dtypes


# In[30]:


# trasformo le colonne numeriche
numeric_cols = ["viewCount","likeCount","favouriteCount","commentCount"]
df_video[numeric_cols] = df_video[numeric_cols].apply(pd.to_numeric, errors = "coerce", axis = 1) 


# In[31]:


# modifico formattazzione della data di pubblicazione e creo giorno settimana
df_video["publishedAt"] = df_video["publishedAt"].apply(lambda x: parser.parse(x))
df_video["publishDayName"] = df_video["publishedAt"].apply(lambda x: x.strftime("%A"))
df_video[["publishedAt","publishDayName"]]


# In[32]:


# formatto durata
df_video["durationSecs"] = df_video["duration"].apply(lambda x: isodate.parse_duration(x))
df_video["durationSecs"]


# In[33]:


# trasformo durata in secondi
df_video["durationSecs"] = df_video["durationSecs"].dt.total_seconds()
df_video["durationSecs"]


# In[34]:


df_video["tagCount"] = df_video["tags"].apply(lambda x: 0 if x is None else len(x))
df_video["tagCount"]


# In[35]:


ax = sns.barplot(x='title', y='viewCount' , data = df_video.sort_values(
    'viewCount',
    ascending = False)[0:19]
                )
plot = ax.set_xticklabels(ax.get_xticklabels(),rotation = 90)

import matplotlib.ticker as ticker  
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos:'{:,.0f}'.format(x/1000)+'K'))


# In[42]:


plot = sns.violinplot(data = df_video, y = df_video["viewCount"], orient = "o")
plot.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos:'{:,.0f}'.format(x/1000)+'K'))


# In[43]:


fig,ax = plt.subplots(1,2)
sns.scatterplot(data = df_video, x = "commentCount", y = "viewCount", ax = ax[0])
sns.scatterplot(data = df_video, x = "likeCount", y = "viewCount", ax = ax[1])


# In[47]:


sns.histplot(data = df_video, x = "durationSecs", bins = 30)


# In[ ]:




