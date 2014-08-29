import urllib


def request(url, params):
    data = urllib.parse.urlencode(params)
    req = urllib.request.Request(url, data)
    response = urllib.request.urlopen(req)
    the_page = response.read()
    return the_page
