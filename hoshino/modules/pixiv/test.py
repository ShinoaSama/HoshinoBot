from hoshino import aiorequests
import requests

setu_get_url = "https://api.lolicon.app/setu/"
setu_APIKEY = '193416775ed3983f2aa954'


def setu_api_request():
    params = {'apikey': setu_APIKEY, 'size1200': True}
    resp = requests.get(setu_get_url, params).json()
    if len(resp['data']) == 0:
        return None

    image_data = resp['data'][0]

    image_pid = image_data['pid']
    image_title = image_data['title']
    image_author = image_data['author']
    image_cqcode = '[CQ:image,timeout=10,file=%s]' % (image_data['url'])
    image_tags = ",".join(image_data['tags'])

    wrapped_message = "pid: %s\n" % image_pid + \
                      "title: %s\n" % image_title + \
                      "author: %s\n" % image_author + \
                      "%s\n" % image_cqcode + \
                      "tags: %s" % image_tags
    return wrapped_message

if __name__ == "__main__":
    msg = setu_api_request()
    print(msg)
