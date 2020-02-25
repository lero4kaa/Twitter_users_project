import os
os.environ["MAPQUEST_API_KEY"] = "w89COg4k1MUAjuvVeSwLaNclGg0nWKf9"
import urllib.request
import urllib.parse
import urllib.error
import twurl
import json
import ssl
import geocoder
import folium


def find_coordinates(address):
    """
    str -> float, float
    Function returns coordinates of given address.
    >>> find_coordinates('London, UK')
    (51.50015, -0.12624)
    """
    if address is not None:
        coordinates = geocoder.mapquest(address)
        lat = coordinates.json['lat']
        lng = coordinates.json['lng']
        return lat, lng
    else:
        return None, None


def getting_json(acct, cursor, tweet_url, ctx):
    """
    Function sends request to Twitter and gets json object
    and returns it.
    """
    if cursor == 1:
        url = twurl.augment(tweet_url,
                            {'screen_name': acct, 'count': '100'})
    else:
        url = twurl.augment(tweet_url,
                            {'screen_name': acct, 'count': '100',
                             'cursor': '{}'.format(cursor)})
    print('Retrieving', url)
    try:
        connection = urllib.request.urlopen(url, context=ctx)
        data = connection.read().decode()
        js = json.loads(data)
        with open("result_json1.txt", mode="w", encoding="utf-8") as f:
            json.dump(js, f, indent=4, ensure_ascii=False)
        headers = dict(connection.getheaders())
        if headers['x-rate-limit-remaining'] == '0':
            print("Sorry, current API key can`t make more requests."
                  "Not all friends will be present on your map.")
            return js, headers['x-rate-limit-remaining']

        print('Remaining', headers['x-rate-limit-remaining'])
        return js, headers['x-rate-limit-remaining']
    except urllib.error.HTTPError:
        print("This account does not exist. Try again")
        return None, None


def main(acct):
    """
    Function gets username and generates html-file with a map
    of user`s friends locations.
    """
    twitter_url = 'https://api.twitter.com/1.1/friends/list.json'

    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    m = folium.Map()
    cursor = 1
    remains = 1
    loc_name_dict = dict()
    while cursor != 0 and remains != '0':
        js, remains = getting_json(acct, cursor, twitter_url, ctx)
        if js is None:
            print("returned None")
            return None

        friends = js['users']
        for i in range(len(friends)):
            location = friends[i]['location']
            name = friends[i]['screen_name']
            loc_name_dict[name] = location
        cursor = js['next_cursor']

    fg_users = folium.FeatureGroup(name="Users")
    used_coordinates = set()
    for element in loc_name_dict.keys():
        if loc_name_dict[element] == "":
            continue
        lat, lng = find_coordinates(loc_name_dict[element])
        while True:
            if (lat, lng) not in used_coordinates:
                used_coordinates.add((lat, lng))
                break
            else:
                lat, lng = lat + 0.0001, lng + 0.0001

        fg_users.add_child(folium.Marker([lat, lng],
                                         popup="{}".format(element),
                                         icon=folium.Icon()))

    m.add_child(fg_users)

    m.save('/home/valeriia13/mysite/templates/map_with_friends.html')

    return "You can see map at map_with_friends.html"


if __name__ == "__main__":
    username = input("Please enter username")
    main(username)
