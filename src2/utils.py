import os 
import subprocess 
import logging 
import datetime 
import re 
import pandas as pd 
import json 
from fuzzywuzzy import fuzz
import numpy as np 
# class for utilities things 

class utils:
    def __init__(self) -> None:
        pass
    def dummy(self):
        print('this is utils')
    
    # returns absolute path for directories behind *args, for exmplae path_join('tmp','vids') will point to ./tmp/vids/
    def path_join(self,*args,ext='',meta=False,swap=False):     
        path_join = lambda l : os.path.join(current_dir,*l).replace('\\','\\\\')+ext
        if swap:        # swaps a  file in provided fp  
            fp=args[0]
            swap=args[1]
            isfile=os.path.isfile(fp)
            if not isfile:                          # if file does not exist 
                print(f'{fp} file does not exist')
                return None 
            base=os.path.dirname(fp)+'\\\\'
            return os.path.join(base,swap)
            
                   
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path=path_join(args)
        isfile=os.path.isfile(path)
        isdir=os.path.isdir(path)
        exist=os.path.exists(path)
        if meta:    # if meta returns metadata about filepath 
            return path.replace('\\\\\\','\\\\'), {'isfile':isfile,'isdir':isdir,'exists':exist}
        path=path.replace('\\\\\\','\\\\')

        return path
    
    # sets up logger object for logging 
    def setup_logger(self,name, log_file, level=logging.INFO,mode='w'):
        log_fp=self.path_join('tmp','logs',log_file)
        print(log_fp)

        handler = logging.FileHandler(log_fp,mode=mode,encoding="utf-8")        
        BASIC_FORMAT = "%(levelname)s:%(name)s:%(message)s"  
        formatter=logging.Formatter(BASIC_FORMAT)
        handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        self.log_variable(logger,msg=' logger setup ')
        return logger
    
    # wrapper for better logging 
    def log_variable(self,logger,msg='',lvl='info',**kwargs):
        ts=datetime.datetime.now().isoformat()
        s=f'{msg} {ts}'
        for k,v in kwargs.items():
            s+= f'\n{k} : {v}'
        if lvl=='warning':
            logger.warning(s)
        else:
            logger.info(s)
    
    # wrapper for subprocess utility 
    def subprocess_run(self,l,**kwargs):
        try:
            q=subprocess.run(l,capture_output=True, text=True,shell=True)
            self.log_variable(logger=self.logger, msg='subprocess run query', q=q)
        except Exception as err:
            print(err)
            self.log_variable(logger=self.logger, msg=' error when executing subprocess query ',lvl='warning',err=err,q=q)
            return 
        if  q.returncode==0:
            return q.stdout.strip()
        else:
            print('dupa!')
            self.log_variable(logger=self.logger, msg=' returncode from subprocess != 0 ',lvl='warning',q=q)
        return q.returncode
    
    
    def extract_sound_from_vid(self,vid_fp,timestamps=None,out_fp=None):
        self.ffmpeg_path="C:\\ffmpeg\\bin\\"
        ffmpeg=[f"{self.ffmpeg_path}ffmpeg"] # ffmpeg executable  

        l=['-i',f'{vid_fp}','-ss',f'{timestamps[0]}','-t',f'{timestamps[1]}','-q:a','0','-map','a',f'{out_fp}']
        l=ffmpeg + l 
        
        self.subprocess_run(l=l)
        
        
    
    
    # parses yt url into stuff depending on what it contains 
    def parse_url(self,url : str ) -> dict:
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
    # strips extension from a file and changes it to new_ext 
    def strip_extension_old(self,s: str, new_ext = None ):
        s=s.strip()
        ext_reg=r'^([^.]+)'
        s= re.findall(ext_reg,s)[0]
        if new_ext is None:
            return s 
        s=s+f'{new_ext}'
        return s.replace('..','.')
    
    def strip_extension(self,s : str,new_ext=''):
        s=s.strip()
        reg=r"([^.]+)(?:\.([^.]+))?(?:\.([^.]+))?"
        #match = re.search(r"([^.]+)\.([^.]+)\.([^.]+)", s)
        match=re.search(reg,s)
        core=match.groups(0)[0]+new_ext
        ext=[i for i in match.groups(0)][1:]
        return core,ext
    
    
    # inserts dictionary to a dataframe and clears dictionary 
    def df_insert_d(self,df: pd.DataFrame,d : dict,clear_d=True ):
        df.loc[len(df)]=d 
        if clear_d:
            for k,v in d.items():
                d[k]=None
#        d.clear()
        
    def ts_to_flt(self,s = None): # string timestamp to float 
        #s='00:01:04.200'
        hh,mm,ss,ff=s.replace('.',':').split(':')
        dt=round(float(ff)/1000+float(ss)+float(mm)*60+float(hh)*60*60,3)
        return dt 

    def flt_to_ts(self,ff = None ):
        hh=ff/60/60//1
        mm=(ff-hh*60*60)/60//1
        ss=(ff-hh*60*60-mm*60)//1
        fff=(ff-hh*60*60-mm*60-ss)*1000
        return '{:02d}:{:02d}:{:02d}.{:03d}'.format(int(hh), int(mm), int(ss),int(fff))
    
    # clears tmp directory or other directory 
    def clear_dir(self,fp):
        files=os.listdir(fp)
        for file in files:
            fpp=self.path_join(fp,file)
           
            os.remove(fpp)
    
    
    def clear_tmp(self,*args):
        if args==():
            args=('tmp',)
        fp=self.path_join(*args)
        files=os.listdir(fp)
        for file in files:
            fp,meta=self.path_join(*args,file,meta=True)
            isfile=meta[0]
            if isfile:
                os.remove(fp)

    def read_csv(self,fp):
        df=pd.read_csv(filepath_or_buffer=fp,quoting=1,delimiter='|',index_col=0)
        return df 
        
    def dump_df(self,df,name = None ,fp = None ):
        if fp is None:
            fp=self.path_join(self.tmp_dir,name)
        df.to_csv(path_or_buf=fp,sep='|',quoting=1,mode='w')
        return fp
    
    # makes a directory 
    def make_dir(self,fp):
        if os.path.exists(fp):
            return fp 
            files=os.listdir(fp)
            for file in files:
                    fpp=self.path_join(fp,file)
                    os.remove(fpp)
        
        if not os.path.exists(fp):
            os.makedirs(fp)
        return fp 
    
    
    def concat_on_condition2(self,df,cond = None ):
        df2=pd.DataFrame(columns=df.columns)
        ok_indexes=[0]                  # first row cant be moved up 
        bad_indexes=[]
        df2.loc[0]=df.loc[0].to_dict()  # rewrite first row 
        no=1                            # first row rewritten 
        
        while no<len(df):
            prev_row=df.iloc[no-1].to_dict()
            cur_row=df.iloc[no].to_dict()
            
            if not cond(prev_row,cur_row): # if not condition rewrite row 
                df2.loc[len(df2)]=cur_row
                ok_indexes.append(no)
                no+=1
            else:
                df2.loc[len(df2)]=cur_row   # rewrite the row but also delete it later 
                bad_indexes.append(no)
                last_row=df2.iloc[max(ok_indexes)].to_dict() # last ok row 
                last_row['txt'] = last_row['txt'] + ' ' + cur_row['txt']
                last_row['en_flt'] = cur_row['en_flt']
                df2.iloc[max(ok_indexes)]=last_row
                no+=1
                
        
        df2.drop(bad_indexes,inplace=True)
        print(df2)
            
    def concat_on_condition3(self,df,cond = None,func=None ):
        print(df)
        df2=pd.DataFrame(columns=df.columns)
        ok_indexes=[0]                  # first row cant be moved up 
        bad_indexes=[]
        df2.loc[0]=df.loc[0].to_dict()  # rewrite first row 
        no=1                            # first row rewritten 
        
        while no<len(df):
            prev_row=df.iloc[no-1].to_dict()
            cur_row=df.iloc[no].to_dict()
            
            if not cond(prev_row,cur_row): # if not condition rewrite row 
                df2.loc[len(df2)]=cur_row
                ok_indexes.append(no)
                no+=1
            else:
                prev_row,cur_row,del_bool=func(prev_row,cur_row)  # modify rows 
                if del_bool:
                    bad_indexes.append(no)
                
                df2.loc[len(df2)]=cur_row           # rewrite the row but also delete it later if necessary 
                df2.iloc[max(ok_indexes)]=prev_row  # rewrite previous ok row 
                no+=1
                
        
        df2.drop(bad_indexes,inplace=True)
        print(df2)

    # requires better testing bro 
    # cuts off part of a string that's behind provided fuzzy_string
    def fuzzy_cutoff(self,s,fuzzy_string='dzieki za ogladanie',include_fuzzy_string=False,append_txt=''):
        new_s=[]
        l=s.split(' ')
        N=len(fuzzy_string.split(' '))
        bl=0
        for i in range(0,len(l)-N):
            w=l[i:i+N]
            sentence=' '.join(w)
            ratio = fuzz.token_sort_ratio(sentence, fuzzy_string)
            print(sentence)
            if ratio>80:
                bl=1
                break
            w=[i.strip() for i in sentence.split(' ')]
            new_s.append(w[0])
        if include_fuzzy_string:
            new_s.append(fuzzy_string)
            
        if bl: # append only if match happened 
            new_s.append(append_txt)
        return ' '.join(new_s)  

    # requires better testing bro 
    # returns part of a string that's behind a fuzzy string 
    def fuzzy_startoff(self,s,fuzzy_string='liftvault',include_fuzzy_string=False,prepend_txt=''):
        new_s=[prepend_txt]
        l=s.split(' ')
        N=len(fuzzy_string.split(' '))
        bl=0
        for i in range(0,len(l)):
            w=l[i:i+N]
            sentence=' '.join(w)
            ratio = fuzz.token_sort_ratio(sentence, fuzzy_string)
            if ratio>80:
                bl=1
                if not include_fuzzy_string:
                    continue
            w=[i.strip() for i in sentence.split(' ')]
            if bl:
                new_s.append(w[0])
                

        return ' '.join(new_s)  

#---------------------------------------
import ytd 

def func(prev_row,cur_row):
    txt1=prev_row['txt']
    txt2=cur_row['txt']
    txt1=txt1 +' '+ txt2.split('. ')[0]+'.'
    txt2=' '.join(txt2.split('. ')[1:])
    prev_row['txt']=txt1
    cur_row['txt']=txt2
    return prev_row,cur_row,False
    
def func(prev_row,cur_row):
    prev_row['txt']=prev_row['txt'] + ' '+cur_row['txt']
    prev_row['en_flt']=cur_row['en_flt']
    return prev_row,cur_row,True
    
    
def concat_on_cond2():
    i=ytd.ytd()
    f='concat_on_cond3.csv'
    input_csv=i.path_join('tests','tests_inputs',f)    
    input_df = i.read_csv(fp=input_csv)
    
    cond=lambda prev_row,cur_row : cur_row['txt'] in ['third','fourth']
    cond = lambda prev_row,cur_row : '. ' in cur_row['txt']
    
    i.concat_on_condition3(df=input_df,cond=cond,func=func)
    
    

    
    
if __name__=='__main__':
    concat_on_cond2()