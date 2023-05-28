import os 
import logging 
import datetime 
import subprocess
import shutil
import pandas as pd 
import hashlib 
import pydub 
from moviepy.editor import VideoFileClip, AudioClip
import cv2 
class Utils:
    def __init__(self) -> None:
        self.current_dir=os.path.dirname(os.path.abspath(__file__))
        
    def __str__(self):
        return """ class with static methods that are useful """
        
    @staticmethod
    def path_join_new(*args,ext='',meta=False,swap=False):
        current_dir=os.path.dirname(os.path.abspath(__file__))
        path=os.path.abspath(os.path.join(current_dir,*args))
        print(os.stat(path))
        if meta:
            isfile=os.path.isfile(path)
            isdir=os.path.isdir(path)
            exist=os.path.exists(path)
            return path, {'isfile':isfile,'isdir':isdir,'exists':exist,'fname': os.path.basename(args[0])}
        
        return path 
        
    @staticmethod
    def path_join(*args,ext='',meta=False,swap=False):     
        current_dir=os.path.dirname(os.path.abspath(__file__))
        path_join = lambda l : os.path.join(current_dir,*l).replace('\\','\\\\')+ext
        if swap:                                    # swaps a  file in provided fp  
            fp=args[0]
            swap=args[1]
            isfile=os.path.exists(os.path.abspath(fp))
            if not isfile:                          # if file does not exist 
                print(f'{fp} file does not exist')
                return None 
            base=os.path.dirname(fp)+'\\\\'
            return os.path.join(base,swap)
        path=path_join(args)
        isfile=os.path.isfile(path)
        isdir=os.path.isdir(path)
        exist=os.path.exists(path)
        if meta:                                    # if meta returns metadata about filepath 
            return path.replace('\\\\\\','\\\\'), {'isfile':isfile,'isdir':isdir,'exists':exist,'fname': os.path.basename(args[0])}
        path=path.replace('\\\\\\','\\\\')
        return path
    
    @staticmethod
    def setup_logger(name, log_file, level=logging.INFO,mode='w'):
        """ sets up logger """
        current_dir=os.path.dirname(os.path.abspath(__file__))
        log_fp=Utils().path_join(current_dir,'logs',log_file)
        handler = logging.FileHandler(log_fp,mode=mode,encoding="utf-8")        
        BASIC_FORMAT = "%(levelname)s:%(name)s:%(message)s"  
        formatter=logging.Formatter(BASIC_FORMAT)
        handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        Utils().log_variable(logger,msg=f'logger setup {name}')
        return logger
    
    @staticmethod
    def log_variable(logger,msg='',lvl='info',**kwargs):
        """ my way of logging variables in the log """
        ts=datetime.datetime.now().isoformat()
        s=f'{msg} {ts}'
        for k,v in kwargs.items():
            s+= f'\n{k} : {v}'
        if lvl=='warning':
            logger.warning(s)
        else:
            logger.info(s)
            
    @staticmethod
    def subprocess_run(l,logger=None,**kwargs):
        """try catch wrapper for subprocess run """
        try:
            q=subprocess.run(l,capture_output=True, text=True,shell=True,**kwargs)  
        except Exception as er:
            if logger is not None:
                Utils().log_variable(logger,msg='error in subprocess run',lvl='warning',l=l,er=er)
            pass
            return None,None,None
        
        if logger is not None:
            Utils().log_variable(logger,msg=f'subprocess',l=l)
            
        return q.returncode,q.stdout,q.stderr # returncode, stdout, stderr 
        
    @staticmethod
    def get_cur_ts(format="%Y%m%d%H%M%S"):
        return datetime.datetime.now().strftime(format) # "%Y%m%d%H%M" format for minutes
    
    @staticmethod
    def flt_to_ts(ff : float): # float to timestamp string
        if ff != ff: # float is nan:
            ff=0
        hh=ff/60/60//1
        mm=(ff-hh*60*60)/60//1
        ss=(ff-hh*60*60-mm*60)//1
        fff=(ff-hh*60*60-mm*60-ss)*1000
        return '{:02d}:{:02d}:{:02d}.{:03d}'.format(int(hh), int(mm), int(ss),int(fff))
    
    @staticmethod
    def clean_txt(s : str,**kwargs): # cleans up string 
        custom_d={k:v for k,v in kwargs.items()}
        translation_table = str.maketrans({'\xa0': ' ', '\n': ' ', '\t': ' ', '\r': ' ','\u200b':''})
        translation_table.update(custom_d)
        translation_table[ord("\n")] = " "
        clean_string = s.translate(translation_table)
        return clean_string.strip().replace('  ',' ')
    
    @staticmethod
    def df_insert_d(df: pd.DataFrame, d : dict,clear_d=True ):
        df.loc[len(df)]=d 
        if clear_d:
            for k,v in d.items():
                d[k]=None
    
    @staticmethod 
    def make_dir(fp,delete_flg=False):
        # makes a directory and by default deletes the old one
        if os.path.exists(fp):
            if delete_flg:
                shutil.rmtree(fp)
#            else:
#                os.rename(fp,fp+'_old_'+Utils().get_cur_ts())
        else:
            os.makedirs(fp)
    @staticmethod 
    def clean_dir(fp):
        if os.path.exists(fp):
            for file in os.listdir(fp):
                os.remove(os.path.join(fp,file))
        else:
            print(f'no such directory {fp}')
            
            
            
    @staticmethod
    def dump_df(df,fp,name='df'):
        print(fp)
        fp=os.path.join(fp,name+'.csv')
        df.to_csv(path_or_buf=fp,sep='|',quoting=1,mode='w',index=False)
    
    @staticmethod
    def read_df(fp,**kwargs):
        fp=os.path.join(fp,*[str(x) for x in kwargs.values()])
        return pd.read_csv(fp,sep='|',quoting=1,index_col=0)




    @staticmethod 
    def hash(s):
        return hashlib.sha256(s.encode()).hexdigest()
        
    @staticmethod
    def get_media_len(media_fp): # this method should probably be in vid maker class but i need it in azure tts -,- 
        try:
            l  = len(pydub.AudioSegment.from_file(media_fp))/1000
        except Exception as err:
            print(err)
            clip = VideoFileClip(media_fp)
            l = clip.duration
            
        return l
        
    @staticmethod
    def sentesize(df):
        def clear_df(df=df,func=None):
            for no,row in df.iterrows():
                row=row.to_dict()
                row['txt']=func(row['txt'])
                df.loc[no]=row
        def func(s):
            return s.replace('  ',' ')
            s=s.capitalize()
            if s[-1]=='.':
                return s 
            else:
                return s+'.'    
        clear_df(df=df,func=func)
        
    @staticmethod
    def get_vid_fps(vid_fp):
        cap = cv2.VideoCapture(vid_fp)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        return fps 