# YouTube Analytics API & SendGrid で YouTube のアナリティクスを毎週自動送信
import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import csv
import time
from datetime import datetime, timedelta
import pytz

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, ContentId)

# Number of Results
results = 10
# Mail Counter
mail_send_time = 1

SCOPES = ['https://www.googleapis.com/auth/yt-analytics.readonly']

API_SERVICE_NAME = 'youtubeAnalytics'
API_VERSION = 'v2'
CLIENT_SECRETS_FILE = 'YouTube OAuth Key (.json)'

def get_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def execute_api_request(client_library_function, **kwargs):
    global rows
    response = client_library_function(
        **kwargs
    ).execute()

    rows = response[u'rows']
    print(rows)

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    youtubeAnalytics = get_service() # OAuth

    while True:
        try:
            #date
            day_before_yesterday = datetime.strftime(datetime.now(tz=pytz.timezone('Asia/Tokyo')) - timedelta(2), '%Y-%m-%d')
            nine_day_ago = datetime.strftime(datetime.now(tz=pytz.timezone('Asia/Tokyo')) - timedelta(9), '%Y-%m-%d')
            execute_api_request(
                youtubeAnalytics.reports().query,
                ids='channel==MINE',
                maxResults = str(results),
                startDate=nine_day_ago,
                endDate=day_before_yesterday,
                metrics='views,likes,subscribersGained,subscribersLost',
                dimensions='video',
                sort='-views'
            )

            # Convert Video ID -> Video Title
            api_key = "YouTube Data API Key"
            my_youtube = build("youtube","v3",developerKey=api_key)
            video_titles=[]
            i = 0
            while i < results:
                request = my_youtube.videos().list(part="snippet,contentDetails,statistics", id=rows[i][0])
                response = request.execute()
                video_titles.append(response['items'][0]['snippet']['title'])
                i = i + 1

            # mail
            message = Mail(
                from_email='FROM(mail address)',
                to_emails='TO(mail address)',
                subject='My YouTube Report (' + nine_day_ago + '-' + day_before_yesterday + ')',
                html_content='<table><tr><th>video</th><th>view</th><th>likes</th><th>+Subsc</th><th>-Subsc</th></tr><tr><td>'+video_titles[0]+'</td><td>'+str(rows[0][1])+'</td><td>'+str(rows[0][2])+'</td><td>'+str(rows[0][3])+'</td><td>'+str(rows[0][4])+'</td></tr><tr><td>'+video_titles[1]+'</td><td>'+str(rows[1][1])+'</td><td>'+str(rows[1][2])+'</td><td>'+str(rows[1][3])+'</td><td>'+str(rows[1][4])+'</td></tr><tr><td>'+video_titles[2]+'</td><td>'+str(rows[2][1])+'</td><td>'+str(rows[2][2])+'</td><td>'+str(rows[2][3])+'</td><td>'+str(rows[2][4])+'</td></tr><tr><td>'+video_titles[3]+'</td><td>'+str(rows[3][1])+'</td><td>'+str(rows[3][2])+'</td><td>'+str(rows[3][3])+'</td><td>'+str(rows[3][4])+'</td></tr><tr><td>'+video_titles[4]+'</td><td>'+str(rows[4][1])+'</td><td>'+str(rows[4][2])+'</td><td>'+str(rows[4][3])+'</td><td>'+str(rows[4][4])+'</td></tr><tr><td>'+video_titles[5]+'</td><td>'+str(rows[5][1])+'</td><td>'+str(rows[5][2])+'</td><td>'+str(rows[5][3])+'</td><td>'+str(rows[5][4])+'</td></tr><tr><td>'+video_titles[6]+'</td><td>'+str(rows[6][1])+'</td><td>'+str(rows[6][2])+'</td><td>'+str(rows[6][3])+'</td><td>'+str(rows[6][4])+'</td></tr><tr><td>'+video_titles[7]+'</td><td>'+str(rows[7][1])+'</td><td>'+str(rows[7][2])+'</td><td>'+str(rows[7][3])+'</td><td>'+str(rows[7][4])+'</td></tr><tr><td>'+video_titles[8]+'</td><td>'+str(rows[8][1])+'</td><td>'+str(rows[8][2])+'</td><td>'+str(rows[8][3])+'</td><td>'+str(rows[8][4])+'</td></tr><tr><td>'+video_titles[9]+'</td><td>'+str(rows[9][1])+'</td><td>'+str(rows[9][2])+'</td><td>'+str(rows[9][3])+'</td><td>'+str(rows[9][4])+'</td></tr></table>')
            print(message)
            try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                response = sg.send(message)
                print(response.status_code)
                print("Send Mail Completed! send_time： " + str(mail_send_time))
                mail_send_time = mail_send_time + 1
            except Exception as e:
                print(e.message)
        
        #except:
        except AssertionError as error:
            print("error！ send_time： " + str(mail_send_time) + "(not send mail)")
            print(error)

        time.sleep(900) #15min 
