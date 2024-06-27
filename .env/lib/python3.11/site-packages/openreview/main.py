import requests
import re
import urllib.parse
from datetime import datetime
from openreview.const import NOTE_URL, FORUM_URL

# (\$)([\w\D\W]*?)(\$) remove latex symbol
# 

def extract_forum(id, limit=100, offset=0, remove_latex=False):

    details = 'replyCount,original'
    invitation = urllib.parse.quote(id, safe='')
    url = '{}?invitation={}&details={}&limit=1000&offset=0'.format(NOTE_URL, invitation, details)
    res = requests.request("GET", url, headers={
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
        'Sec-Fetch-Site': 'same-origin',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    })
    if res.status_code == requests.codes.ok:
        data = res.json()
        if 'notes' not in data:
            return []
        results = []
        for note in data['notes']:
            content = note['content']

            created = datetime.utcfromtimestamp(int(note['tcdate'])/1000) if note['tcdate'] else None
            modified = datetime.utcfromtimestamp(int(note['tmdate'])/1000) if note['tmdate'] else None
            deleted = datetime.utcfromtimestamp(int(note['tddate'])/1000) if note['tddate'] else None
            if remove_latex:
                content['abstract'] = re.sub( '(\$)([\w\D\W]*?)(\$)' ,'',content['abstract'])
            content['urls'] = '{}/?id={}'.format(FORUM_URL, note['forum'])
            content['datetime'] = {
                'created': created,
                'modified': modified,
                'deleted': deleted,
            }
            results.append(content)
        return results
    raise Exception('Connection error %d' % res.status_code)


def extract_note(id, trash=True):

    trash = 'true' if trash else 'false'
    details = 'replyCount,writabe,revisions,original,overwriting,tags'
    forum = urllib.parse.quote(id, safe='')
    url = '{}?forum={}&details={}&trash={}'.format(NOTE_URL, forum, details, trash)    
    res = requests.get(url, headers={
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
    })    
    if res.status_code == requests.codes.ok:
        data = res.json()
        if 'notes' not in data:
            return []
        results = []
        for note in data['notes']:
            note['tcdate'] = datetime.utcfromtimestamp(int(note['tcdate'])/1000) if note['tcdate'] else None
            note['tmdate'] = datetime.utcfromtimestamp(int(note['tmdate'])/1000) if note['tmdate'] else None
            note['tddate'] = datetime.utcfromtimestamp(int(note['tddate'])/1000) if note['tddate'] else None
            results.append(note)
        return results
    return []