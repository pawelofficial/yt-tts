import os 
import json 
import pandas as pd 
import numpy as np 
import re 
import datetime
import Utils 
import ytURL
import chardet 


class ytDownloader:
    def __init__(self,utils,ytURL):               
        self.utils=utils
        self.ytURL   = ytURL       # attribute for youtube url with some other stuff behind it 
        self._url    = None        # url provided by user 
        self._tmp_dir = None       # tmp directory      
        self._logger  = None       # logger 
        
        self.logger='ytd_logger'
        self.subs_exist=False       # set by download_subs 
        self.subs_fp=None           # set by download_subs 
        self.vid_exist=False       # set by download_vid
        self.vid_fp=None           # set by download_vid
        self.vid_title=None
        self.tmp_dir=None

        self.subs_df_exist = False  # set by parse subs 
        self.subs_df_fp    = None   # set by parse subs 
        self.subs_df       = None   # actual subs df 

    @property 
    def url(self):
        return self._url
    @url.setter 
    def url(self,url):
        self.ytURL.url=url
        self._url = self.ytURL._parse_url(url)['vid_url']
    @property 
    def tmp_dir(self):
        return self._tmp_dir
    @tmp_dir.setter 
    def tmp_dir(self,dir):
        if dir is None:                                         # if variable was not set 
            dir=datetime.datetime.now().strftime("%Y%m%d%H")
        self._tmp_dir = self.utils.path_join('tmp',dir)
        self.utils.make_dir(fp=self._tmp_dir) 
    @property 
    def logger(self):
        return self._logger    
    @logger.setter 
    def logger(self,nm='ytd_logger'):
        self._logger = self.utils.setup_logger(name=nm,log_file=f'{nm}.log')

    # downloads a vid from yt  
    def download_vid(self,timestamps = None,format='.webm' ):
        vid_url=self.ytURL.vid_url
        l=["yt-dlp","--skip-download",vid_url,"--get-title"]
        returncode, stdout, stderr =self.utils.subprocess_run(l,logger=self.logger) 
        title=stdout.replace(' ','_').replace('|','') + f'.{format}' # yt vid extension is webm 
        title=''.join([c for c in title if c.isalnum() or c in ('_') ])
        fp=self.utils.path_join(self.tmp_dir,title)
        l=["yt-dlp",'--no-cache-dir',vid_url,"-o", f"{fp}"]
        if timestamps is not None:
            l+=["--download-sections",f"*{timestamps[0]}-{timestamps[1]}"]
        returncode, stdout, stderr = self.utils.subprocess_run(l,logger=self.logger)

        self.utils.log_variable(logger=self.logger,msg='destination of video',returncode=returncode,stdout=stdout,stderr=stderr)
        
        filename=title +f'.{format}'
        filename=filename.replace('..','.')    
        vid_fp,meta=self.utils.path_join(self.tmp_dir,filename,meta=True)   # check if file exists 
        self.utils.log_variable(logger=self.logger,msg='downloading video ',filename=filename,meta=meta,returncode=returncode,stdout=stdout,stderr=stderr)
        
        self.vid_exists=meta['exists'] # update state variables 
        self.vid_fp=vid_fp

        if meta['exists']:             
            self.subs_fp=vid_fp
        return vid_fp
            
    # returns bool of whether lang is available and dictionary with available langs and formats 
    def check_available_subs_langs(self,lang):
        vid_url=self.ytURL.vid_url
        l=["yt-dlp","--skip-download",vid_url,"--list-subs"]    
        returncode, stdout, stderr =self.utils.subprocess_run(l,logger=self.logger) 
        langs_d={}
        isavailable = False 
        for line in stdout.splitlines():
            if 'json3' not in line: # skip lines that do not specify language 
                continue
            line=[i.strip() for i in line.split(' ') if i!='']
            ytlang=line[0]
            lang_long=line[1] # not used 
            formats_available=line[1:]
            langs_d[ytlang]=[formats_available]
        isavailable=any([lang == k for k in langs_d.keys()]) # check if lang is available
#        for k,v in langs_d.items():
#            if lang==k or k=='en':
#                isavailable=True
#                print(f'lang {lang} is available')

        self.utils.log_variable(logger=self.logger,msg='available subs',langs_d=langs_d)
        return isavailable, langs_d
            
    # download subs from yt 
    def download_subs(self,lang = 'pl', format='json3' ):
        vid_url=self.ytURL.vid_url
        
        isavailable, langs_d = self.check_available_subs_langs(lang=lang)
        if not isavailable:
            self.utils.log_variable(logger=self.logger,msg=f'lang {lang} is not available',langs_d=langs_d)
            print('lang is not available')
            return None


            
        
        l=["yt-dlp","--skip-download",vid_url,"--get-title"]
        returncode, stdout, stderr =self.utils.subprocess_run(l,logger=self.logger) 
        title=stdout.replace(' ','_').replace('|','').strip() 
        title=''.join([c for c in title if c.isalnum() or c in ('_') ])
        self.vid_title=title
        fp=self.utils.path_join(self.tmp_dir,title)
        l=["yt-dlp","-o", f"{fp}","--skip-download"]
        l+=[vid_url,"--force-overwrites",
            "--no-write-subs",  
            "--write-auto-sub",
            "--sub-format",format,
            "--sub-langs",lang] # en.* might be better here 
        returncode, stdout, stderr  = self.utils.subprocess_run(l,logger=self.logger)
        filename=title +f'.{lang}.{format}'                                 # subs filename 
        subs_fp,meta=self.utils.path_join(self.tmp_dir,filename,meta=True)   # check if file exists 
        self.utils.log_variable(logger=self.logger,msg='downloading subs ',filename=filename,meta=meta,returncode=returncode,stdout=stdout,stderr=stderr)
        
        self.subs_exist=meta['exists'] # update state variables         
        self.subs_fp=subs_fp

    # parses json 
    def _parse_json_pld(self,p,no):
        subs_d={}
        subs_d['no']=no
        subs_d['st_flt']=np.round(int(p['tStartMs'])/1000.0,2)
        if 'dDurationMs' not in p.keys():       # some rows don't have this key 
            subs_d['en_flt']=subs_d['st_flt']+0
        else:
            subs_d['en_flt']=np.round(subs_d['st_flt']+int(p['dDurationMs'])/1000.0,2)
            
        subs_d['st']=self.utils.flt_to_ts(ff=subs_d['st_flt'])
        subs_d['en']=self.utils.flt_to_ts(ff=subs_d['en_flt'])
        txt=' '.join([d['utf8'] for d in p['segs'] if d['utf8']!='\n']  ).replace('  ',' ').strip()
        
        rs=[r'\[.*\]',r"^,|,$",r"^\[\w+",r"[aA-zZ]*\]"] # clean up stuff from yt 
        for r in rs:
            txt=re.sub(r,'',txt).replace('[','').replace(']','') # 
        subs_d['txt']=self.utils.clean_txt(txt)
        return subs_d
        
    # calculates pause to next on a dataframe 
    def _calculate_pause_to_next(self,df):
        a=df['en_flt']
        b=df['st_flt'].shift(-1)
        df['pause_flt']=np.round(b-a,2)
        #df.loc[df.index[-1],'pause_flt']=0
        df['dif']=np.round(df['en_flt']-df['st_flt'],2)

    # concats rows in df on condition function 
    def _concat_on_condition(self,df,cond = None,func=None ):
        df=df.copy(deep=True)
        no=1                            
        df['index']=df.index
        while no<len(df):
            self._calculate_pause_to_next(df=df)
            prev_row=df.iloc[no-1].to_dict()
            cur_row=df.iloc[no].to_dict()
            c=cond(prev_row,cur_row)
            #print(prev_row)
            #print(cur_row,' ',c)
            if not c:
                no+=1
            else:
                prev_row,cur_row,bl = func(prev_row,cur_row)
                #print(f'    {prev_row}')
                #print(f'    {cur_row}')
                df.loc[prev_row['index']]=prev_row
                df.loc[cur_row['index']]=cur_row
                if bl:
                    df.drop(cur_row['index'],inplace=True)
                    no-=1
                no+=1
        df.drop('index',axis=1,inplace=True)
        return df
    
    # parses json3 mess subs to a nice df 
    def parse_json3_to_df(self):
        cols=['no','st','en','st_flt','en_flt','dif','pause_flt','txt']
        subs_d={k:None for k in cols}  
        with open(self.subs_fp,'rb') as f:
            raw_data=f.read()
        encoding=chardet.detect(raw_data)['encoding']
        
        with open(self.subs_fp,'r',encoding=encoding) as f:
            pld=json.load(f)['events']                  # read data to list 
        pld=[i for i in pld if 'segs' in i.keys()]      # remove items without text 
        tmp_df=pd.DataFrame(columns=subs_d.keys())      # declare temporary df 
        for no,p in enumerate(pld):                     # insert data to temporary df 
            subs_d=self._parse_json_pld(p=p,no=no)
            txt=subs_d['txt'].strip()
            if txt not in ['']:                         # don't write empty rows 
                self.utils.df_insert_d(df=tmp_df,d=subs_d)
        tmp_df['dif']=np.round(tmp_df['en_flt']-tmp_df['st_flt'],2 ) # calculate dif col 
        self._calculate_pause_to_next(df=tmp_df)
        self.subs_df=tmp_df                             # replace subs_df with new df 

    # concats df on condition function between current and previous row 
    def concat_overlapping_rows(self,N=0,sentesize = False):    
        def func(prev_row,cur_row): # func summing cur row to previous row 
            prev_row['txt']=prev_row['txt']+' ' + cur_row['txt']
            prev_row['en_flt']=cur_row['en_flt']
            prev_row['en']=cur_row['en']
            return prev_row,cur_row,True
        cond=lambda prev_row,cur_row  :  cur_row['st_flt']<=prev_row['en_flt']+N
        
        self.subs_df=self._concat_on_condition(df=self.subs_df,cond=cond,func=func)
        if sentesize:
            self.utils.sentesize(df=self.subs_df)
        self._calculate_pause_to_next(df=self.subs_df)
    # concats df on more or less N secondy chunks 
    def concat_on_time(self,N=60):
        def func(prev_row,cur_row): # func summing cur row to previous row 
            prev_row['txt']=prev_row['txt']+' ' + cur_row['txt']
            prev_row['en_flt']=cur_row['en_flt']
            prev_row['en']=cur_row['en']
            return prev_row,cur_row,True
        cond=lambda prev_row,cur_row  :  cur_row['st_flt']//N== prev_row['st_flt']//N
        self.subs_df=self._concat_on_condition(df=self.subs_df,cond=cond,func=func)
        self.utils.sentesize(df=self.subs_df)
        self._calculate_pause_to_next(df=self.subs_df)
    def concat_to_line(self):
        def func(prev_row,cur_row): # func summing cur row to previous row 
            prev_row['txt']=prev_row['txt']+' ' + cur_row['txt']
            prev_row['en_flt']=cur_row['en_flt']
            prev_row['en']=cur_row['en']
            return prev_row,cur_row,True
        cond=lambda prev_row,cur_row  :  True
        self.subs_df=self._concat_on_condition(df=self.subs_df,cond=cond,func=func)
        self.utils.sentesize(df=self.subs_df)
        self._calculate_pause_to_next(df=self.subs_df)


    # returns dictionary with chunks of text aggregated to more or less N second lengths 
    def get_chunks_of_subs(self,N=5*60): 
        msk=self.subs_df['en_flt']//N         
        l=list(set(msk.to_list()))
        chunks_d={}
        for i in l:
            msk=self.subs_df['en_flt']//N==i
            st_flt=min(self.subs_df['st_flt'][msk])
            en_flt=max(self.subs_df['en_flt'][msk])
            s=' '.join(self.subs_df['txt'][msk].to_list())
            s=self.utils.clean_txt(s)
        
            chunks_d[str(int(i))]={'st_flt':st_flt,'en_flt':en_flt,'chunk':s}
            #print(chunks_d[str(int(i))])
        return chunks_d
        
        
        
    
        

if __name__=='__main__':
    print('here')
    url='https://www.youtube.com/watch?v=wVvhBr64odI&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=LoQkO6LaETA&ab_channel=S%C5%82awomirMentzen'
#    url='https://www.youtube.com/watch?v=kQKrmDLvijo&ab_channel=eltoro'
#    url='https://www.youtube.com/watch?v=vdnA-ESWcPs&t=13s&ab_channel=Movieclips'
#    #url='https://youtube.com/clip/Ugkx18gY1IHB--ovOGIXSlfMNFqufyhFT8x1'
#    url='https://www.youtube.com/watch?v=vdnA-ESWcPs&t=13s&ab_channel=Movieclips'
    url='https://www.youtube.com/watch?v=_lOT2p_FCvA&ab_channel=StarWarsMalaysia'
    utils=Utils.Utils()
    yturl=ytURL.ytURL()
    ytd=ytDownloader(utils=utils,ytURL=yturl)
    ytd.url=url                              
    ytd.tmp_dir=ytd.utils.get_cur_ts()       
    timestamps=["00:01:55","00:02:05"]
    timestamps=["00:00:53","00:01:30"]
    timestamps=None
    ytd.download_vid( timestamps=timestamps)                      
    