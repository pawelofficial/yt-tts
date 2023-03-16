import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import ytDownloader
import Utils
import ytURL

def set_ytd():
    utils=Utils.Utils()
    yturl=ytURL.ytURL()
    ytdownloader=ytDownloader.ytDownloader(utils=utils,ytURL=yturl)
    return ytdownloader,utils,yturl


def test_setters(url = None):
    if url is None:
        url='https://www.youtube.com/watch?v=GQ-k8i7qkMw&ab_channel=KinoCheck.com'
    ytdownloader,utils,yturl=set_ytd()
    yturl.url=url
    print(yturl.vid_url)
    print(yturl.channel)
    print(yturl.channel_url)
    print(yturl.url_d)
    
    
    

    
    
if __name__=='__main__':
    test_setters()
#    test_parse_url(url='https://www.youtube.com/@KinoCheck.com')