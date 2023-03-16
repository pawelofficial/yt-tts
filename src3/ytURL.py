import re 


class ytURL:
    def __init__(self) -> None:

        self._url=None # user provided yt url this class tries to par

        self._vid_url = None 
        self._channel=None 
        self._channel_url = None 
        self._url_d=None

        
    @property
    def url(self):
        return self._url        
    
    @url.setter
    def url(self,yt_url):
        self._url=yt_url
        self._parse_url(url=yt_url)

        self._vid_url=self._parse_url(url=yt_url)['vid_url']
        self._channel=self._parse_url(url=yt_url)['channel']
        self._channel_url=self._parse_url(url=yt_url)['channel_url']    
        self._url_d=self._parse_url(url=yt_url)
        
        

             
    @property 
    def vid_url(self):
        return self._vid_url
    @vid_url.setter
    def vid_url(self,url):
        self._vid_url=self._parse_url(url=url)['vid_url']
        
    @property
    def channel(self):
        return self._channel
    @channel.setter
    def channel(self,url):
        self._channel=self._parse_url(url=url)['channel']
        
    @property
    def channel_url(self):
        return self._channel_url
    @channel_url.setter
    def channel_url(self,url):
        self.channel_url=self._parse_url(url=url)['channel_url']
    
    @property
    def url_d(self):
        return self._url_d
    @url_d.setter
    def url_d(self,url):
        self._url_d=self._parse_url(url=url)    
    
    

    def _parse_url(self,url) -> dict:
        id_reg=r'v=([^&]+)'
        channel_reg=r'ab_channel=(.*)|(\@.*)'
        vid_reg=r'\&ab_channel.*'
        vid_reg=r'watch\?v=([aA0-zZ9]+)'
        base_reg=r'(.*com/)'    
        id=re.findall(id_reg,url)
        #print('id: ', id)
        channel=re.findall(channel_reg,url)
        #print('channel: ',channel)
        vid_url=re.findall(vid_reg,url)
        base_url=re.findall(base_reg,url)[0]
        channel_url = None 
        vid_url = None 

        if id==[]:
            id=None 
        else:
            id=id[0]
        if channel==[]:
            channel=None
        else:
            channel=max(channel[0])
        if id is not None:
            vid_url=base_url+'watch?v='+id 
        if channel is not None:
            channel_url = base_url+channel+'/videos'

        d={"id":id
           ,"channel":channel
           ,"vid_url":vid_url
           ,"channel_url":channel_url
           ,"orig_url":url }
        return d