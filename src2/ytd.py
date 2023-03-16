
from utils import utils 
import os 
import glob 
import re 
import pandas as pd 
from tabulate import tabulate 
import numpy as np 
import json 
import datetime 
class ytd(utils):
    def __init__(self) -> None:
        super().__init__()
        self.logger=self.setup_logger(name='ytd_logger',log_file='ytd.log')
        
        self.tmp_dir=self.path_join('tmp')  # path to tmp dir 
        self.vid_fp=None                            # filepath to video modified by self.download_vid
        self.subs_fp=None                           # modified by                   self.download_subs
        self.cols=['no','st','en','st_flt','en_flt','dif','pause_flt','txt']
        self.subs_d={k:None for k in self.cols}                
        self.tmp_df=pd.DataFrame(columns=self.subs_d.keys())  # temporary subs df during parsing process 
        self.subs_df=pd.DataFrame(columns=self.subs_d.keys()) # final subs df 
        self.pause_flt=0.1                      # pause cutoff for concatenation of subs 
        self.subs_default_lang='en'             # default subs language 
        self.subprocess_out=None                # tracking subprocess execution 
        
    # downloads a vid to tmp directory 
    def download_vid(self,yt_url,timestamps = None ):
        d=self.parse_url(url=yt_url)
        
        l=["yt-dlp","--skip-download",d['vid_url'],"--get-title"]
        raw_title=self.subprocess_run(l).replace(' ','_').replace('|','').upper()
        title=''.join(e for e in raw_title if e.isalnum() or e=='_' )
        fp=self.path_join(self.tmp_dir,title)
        l=["yt-dlp",'--no-cache-dir',d['vid_url'],"-o", f"{fp}"]
        if timestamps is not None:
            l+=["--download-sections",f"*{timestamps[0]}-{timestamps[1]}"]
        self.subprocess_out=self.subprocess_run(l)
        self.vid_fp=fp+'.webm'
        self.vid_fname=title+'.webm'
        return self.vid_fp

    # checks if subs language is available 
    def check_subs_availability(self,yt_url,lang='en-orig') -> bool:
        available_subs=self.get_available_subs(yt_url=yt_url)
        return lang in available_subs.keys(),available_subs
    
    # returns dictionary with info about subs availability 
    def get_available_subs(self,yt_url) -> dict:
        d=self.parse_url(url=yt_url)
        l=["yt-dlp","--skip-download",d['vid_url'],"--list-subs"]
        out=self.subprocess_run(l).splitlines()
        available_subs={}
        available_subs['vid_id']=out[0].split(' ')[1]           # id of video 
        available_subs['has_subs']=out[-1]                      # info it subs are available 
        for line in out[4:-1]:                                  # yeap...
            line2=[i for i in line.split(' ') if i !='']
            available_subs[line2[0]]=line2[1]
        available_subs['full_text']=out
        return available_subs
               
    # downloads subs to /tmp dir
    # returns subs_fp, modifies self.subs_fp
    def download_subs(self,yt_url,lang=None,format='json3'):
        if lang is None:
            lang=self.subs_default_lang
        lang_available,all_langs = self.check_subs_availability(yt_url=yt_url,lang=lang)
        if not lang_available:
            print(f'subs with lang {lang} are unavailable')
            self.log_variable(logger=self.logger,msg=f'subs with lang {lang} are unavailable for {yt_url}',lvl='warning',all_langs=all_langs)
            return None 

        d=self.parse_url(url=yt_url)
        # get title  and remove special chars from it 
        l=["yt-dlp","--skip-download",d['vid_url'],"--get-title"]
        raw_title=self.subprocess_run(l).replace(' ','_').replace('|','').upper()
        title=''.join(e for e in raw_title if e.isalnum() or e=='_' )
        
        fp=self.path_join(self.tmp_dir,title)
        # skip download 
        l=["yt-dlp","-o", f"{fp}","--skip-download"]
        # download subs 
        l+=[d['vid_url'],"--force-overwrites",
            "--no-write-subs",  
            "--write-auto-sub",
            "--sub-format",format,
            "--sub-langs",lang] # en.* might be better here 
        # subs come in various extensions like en.vtt or en.vtt.org so save them as text 
        self.subprocess_out=self.subprocess_run(l)
        myline=[i for i in self.subprocess_out.splitlines() if 'Destination' in i][0]
        self.subs_fp=myline.split(' ')[-1]  
        return self.subs_fp
    
    # cleans txt line  from special chars 
    def _clean_txt(self,s):
        translation_table = str.maketrans("\xa0", " ")
        translation_table[ord("\n")] = " "
        clean_string = s.translate(translation_table)
        return clean_string.strip()
        
    # parses json from youtube into a di tionary              
    def parse_json_pld(self,p : dict,no : int = 0  ):
        subs_d={}
        subs_d['no']=no # int(p['wWinId'])
        subs_d['st_flt']=np.round(int(p['tStartMs'])/1000.0,2)
        if 'dDurationMs' not in p.keys():       # some rows don't have this key 
            subs_d['en_flt']=subs_d['st_flt']+0
        else:
            subs_d['en_flt']=np.round(subs_d['st_flt']+int(p['dDurationMs'])/1000.0,2)
        subs_d['st']=self.flt_to_ts(ff=subs_d['st_flt'])
        subs_d['en']=self.flt_to_ts(ff=subs_d['en_flt'])
        txt=' '.join([d['utf8'] for d in p['segs'] if d['utf8']!='\n']  ).replace('  ',' ').strip()
        # regexs: 1:   stuff between [] like [Muzyka]
                # 2:   strings starting and ending with , 
                # 3,4: broken tags like "[Muzyka"  or "Muzyka]"
        rs=[r'\[.*\]',r"^,|,$",r"^\[\w+",r"[aA-zZ]*\]"] # clean up stuff from yt 
        for r in rs:
            txt=re.sub(r,'',txt).replace('[','').replace(']','') # 
        subs_d['txt']=self._clean_txt(txt)
#        print(subs_d)
#        input('wait')
        return subs_d
                

    # 1st step in subs parsing - reads json into a df 
    # modifies self.tmp_df 
    def read_json3_to_df(self,fp):
        with open(fp,'r',encoding="utf-8") as f:
            pld=json.load(f)['events']                  # read data to list 
        pld=[i for i in pld if 'segs' in i.keys()]      # remove items without text 

        tmp_df=pd.DataFrame(columns=self.subs_d.keys()) # declare temporary df 
        for no,p in enumerate(pld):                                   # insert data to temporary df 
            subs_d=self.parse_json_pld(p=p,no=no)
            txt=subs_d['txt'].strip()
            if txt not in ['']:                         # don't write empty rows 
                self.df_insert_d(df=tmp_df,d=subs_d)
        tmp_df['dif']=np.round(tmp_df['en_flt']-tmp_df['st_flt'],2 ) # calculate dif col 
        self.tmp_df=tmp_df
        self._calculate_pause_to_next(df=self.tmp_df)
        
        return tmp_df
    
    # 4th step in subs parsing 
    def concat_overlapping_rows(self,df,N=0.5):    
        def func(prev_row,cur_row): # func summing cur row to previous row 
            prev_row['txt']=prev_row['txt']+' ' + cur_row['txt']
            prev_row['en_flt']=cur_row['en_flt']
            return prev_row,cur_row,True
        
        cond=lambda prev_row,cur_row  : cur_row['pause_flt']<=N
        df=self._concat_on_condition(df=df,cond=cond,func=func)
        self.sentesize(df=df)
        self.tmp_df=df 
        self._calculate_pause_to_next(df=self.tmp_df)
        return df 
        
    # concat on condition with a function !     
    def _concat_on_condition(self,df,cond = None,func=None ):
        #df2=pd.DataFrame(columns=df.columns)
        ok_indexes=[0]                  # first row cant be moved up 
        bad_indexes=[]
        #df2.loc[0]=df.loc[0].to_dict()  # rewrite first row 
        no=1                            # first row rewritten 
        
        df['index']=df.index
        while no<len(df):
            prev_row=df.iloc[no-1].to_dict()
            cur_row=df.iloc[no].to_dict()
            if not cond(prev_row,cur_row):
                no+=1
            else:
                prev_row,cur_row,bl = func(prev_row,cur_row)
                df.loc[prev_row['index']]=prev_row
                df.loc[cur_row['index']]=cur_row
                
                if bl:
                    df.drop(cur_row['index'],inplace=True)
                    no-=1
                
                no+=1
                
        return df
    
    
    
    # bringing parsing methods together  
    def parse_json3_to_df(self,fp,dump_df=True,N=0.1,**kwargs):
        df=self.read_json3_to_df(fp=fp)                                 # read df
        if kwargs.get('dump_all'):                                      # dump all kwarg 
            self.dump_df(df=df,name='df1_read_json3_to_df.csv')
        
        # 
        df=self.concat_overlapping_rows(df=df,N=N)
        
        if dump_df:
            name=kwargs.get('name')
            if name is None:
                name='df_parsed.csv'
            fp=self.dump_df(df=df,name=name)
            
        self.subs_df=df
        return fp
    
    # calculates pause to next row 
    def _calculate_pause_to_next(self,df):
        a=df['en_flt']
        b=df['st_flt'].shift(-1)
        df['pause_flt']=np.round(b-a,2)
        df.loc[len(df)-1,'pause_flt']=0
        df['dif']=np.round(df['en_flt']-df['st_flt'],2)
        return a-b


    def sentesize(self,df):
        def func(s):
            s=s.capitalize()
            if s[-1]=='.':
                return s 
            else:
                return s+'.'    
        self.clear_df(df=df,func=func)

    def clear_df(self,df,func = None ):
        if func is None:
            func = lambda x: x.replace('  ',' ')
        
        for no,row in df.iterrows():
            row=row.to_dict()
            row['txt']=func(row['txt'])
            df.loc[no]=row
                    


   
# workflow 1 - download and parse subs 
def wf1(ytd: ytd
        ,url='https://www.youtube.com/watch?v=_ypD5iacrnI&ab_channel=MovieRecaps'
        ,download_timestamps=True,
        download_vid=True,
        lang='pl'):

    dir_name=datetime.datetime.now().strftime("%Y%m%d")     # make a dir 
    dir_fp=ytd.path_join(ytd.tmp_dir, dir_name)             # make a dir 
    ytd.make_dir(fp=dir_fp)
    ytd.tmp_dir= dir_fp                                     # set a dir 
    ytd.clear_dir(fp=ytd.tmp_dir)
    if download_vid:
        if download_timestamps:
            timestamps=None # ["00:00:00","00:1:00"]
            ytd.download_vid(yt_url=url,timestamps=timestamps)
        else:
            ytd.download_vid(yt_url=url)
            
    # download whole thing 
    ytd.download_subs(yt_url=url,lang=lang)                 # download subs 
    ytd.parse_json3_to_df(fp=ytd.subs_fp,dump_all=True)     # parse subs, dump all 
    
        
       
       
        
if __name__=='__main__':
    ytd=ytd()
    url='https://www.youtube.com/watch?v=RMeacmRH0wA&t=3s&ab_channel=symmetry'
    url='https://www.youtube.com/watch?v=fhQtKxZ_jL8'
    url='https://www.youtube.com/watch?v=F6dZxoob8CY'
    url='https://www.youtube.com/watch?v=IXQgCASzh3Q'
    url='https://www.youtube.com/watch?v=RMeacmRH0wA&t=3s'
    url='https://www.youtube.com/watch?v=RMeacmRH0wA&t=3s&ab_channel=symmetry'
    url='https://www.youtube.com/watch?v=_ypD5iacrnI'
    url='https://www.youtube.com/watch?v=_yd8dV_7oho&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=VgBpmdULzy0&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=rz-hHjQPaQE&ab_channel=LiftingVault'
    wf1(ytd=ytd
        ,url=url
        ,download_timestamps=False
        ,download_vid=True)
   