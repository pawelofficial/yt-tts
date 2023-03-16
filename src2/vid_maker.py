from utils import utils 
import datetime
import pydub 
import numpy as np 
import time 
from moviepy.editor import *
import torch 
import torchvideo 
import torchvision
import random
import torchaudio
import os 
class vid_maker(utils):
    def __init__(self,today = None ) -> None:
        super().__init__()
        self.logger=self.setup_logger(name='vm_logger',log_file='vm.log')
        self.ffmpeg_path="C:\\ffmpeg\\bin\\"
        self.lambda_make_fp = lambda dir,name: self.path_join(dir,name)
        self.root_dir=self.path_join('tmp')
        
        
        if today is None:
            today=datetime.datetime.now().strftime("%Y%m%d")
         
        self.tmp_dir=self.path_join('tmp',today)        # path to tmp dir
        self.vids_dir=self.path_join(self.tmp_dir,'vids')
        self.background_fp=''                           # fp to background vid
        self.speech_fp=''                               # fp to speech wav 
        self.vid_fp=''                                # fp to video 
        
    # returns len of video in seconds 
    def get_vid_len(self,vid_fp):
        try:
            audio_len=len(pydub.AudioSegment.from_file(vid_fp))/1000
            return audio_len
        except Exception as err:
            clip = VideoFileClip(vid_fp)           
            return clip.duration

    # boomerangizes last n seconds of a video 
    def torch_boomerang(self,vid_fp,out_fp,n=3):
        if n==0:
            n=self.get_vid_len(vid_fp=vid_fp)
        
        vid,audio,info=torchvision.io.read_video(vid_fp)
        start_boomerang_frame= int( len(vid) - n*info['video_fps'] ) 
        if start_boomerang_frame < 0 :
            start_boomerang_frame =0 
        end_boomerang_frame=int( len(vid) ) 
        
        boomerang_tensor=vid[start_boomerang_frame:end_boomerang_frame].clone()
        flip=boomerang_tensor.flip(dims=[0]).clone()
        flip=self.torch_add_effect(t=flip,reverse=False)
        
        boomerang_tensor=self.torch_add_effect(t=boomerang_tensor,reverse=True)
        t=torch.cat(tensors=(vid,flip,boomerang_tensor),dim=0)
        
        torchvision.io.write_video(filename=out_fp
                                   ,video_array=t
                                   ,fps=info['video_fps']
                                   ,video_codec='libvpx')
        return out_fp

    def torch_add_effect(self,t,reverse=False):
        lambda_weight = lambda i,t : i/t.size(0)                # linear scaling of the effect asc  (smooth)
        lambda_weight2=lambda i,t: 1-lambda_weight(i,t)      # linear scaling of the effect desc (abrupt)
        f=lambda_weight
        if reverse:
            f=lambda_weight2
        for i in range(t.size(0)):
            weight=f(i,t)
            t[i,:,:,2]+=int(25*weight) # FHWC RGB make blue channel more blue 

        return t 
        
    def torch_cut_vid(self,vid_fp,out_fp,st_flt = 0 ,en_flt = 10, dur_flt = None ):
        if en_flt==0:                                       # pass zero to get whole video 
            en_flt=self.get_vid_len(vid_fp=vid_fp)
            
        if en_flt <0:                                       # pass negative value to trim from end 
            en_flt=self.get_vid_len(vid_fp=vid_fp)+en_flt
        
        if dur_flt is not None:                             # use duration instead of en_flt with, with precedence 
            en_flt=st_flt+dur_flt
 
        vid,audio,info=torchvision.io.read_video(vid_fp)    # get tensors from video filepath 
        vstart_frame = int(st_flt * info['video_fps'])      # video start frame 
        vend_frame = int(en_flt * info['video_fps'])        # video end frame 

        vclip = vid[vstart_frame:vend_frame]                # video clip tensor 

        torchvision.io.write_video(filename=out_fp
                                   ,video_array=vclip
                                   ,fps=info['video_fps']
                                   ,video_codec='libvpx'
                                   #,audio_array=aclip              # looks like bug in torch  https://stackoverflow.com/questions/75070838/torch-write-video-throws-indexerror
                                   #,audio_fps=info['audio_fps']
                                   #,audio_codec='aac'
                                   )
        return out_fp
        
    def torch_cut_audio(self,audio_fp,out_fp,st_flt = 0 ,en_flt = 10, dur_flt = None ):
        if dur_flt is not None:
            en_flt=st_flt+dur_flt
#        vid,audio,info=torchaudio.io.read_audio(audio_fp)    # get tensors from video filepath 
        waveform, rate_of_sample = torchaudio.load(audio_fp)

        start_sample = int(st_flt *rate_of_sample)      # audio start frame 
        end_sample = int(en_flt * rate_of_sample)        # audio end frame 
        trimmed_waveform = waveform[:, start_sample:end_sample]
        torchaudio.save(out_fp, trimmed_waveform, rate_of_sample)
        return out_fp

    # split sound and video to separate files from a video 
    def split_sound_and_video(self,vid_fp,out_dir,do_audio=True,do_video=False,timestamps=None,out_fp=None,fname=''):
        out_audio_fp=None
        out_video_fp=None

        base=os.path.dirname(vid_fp)
        out_audio_fp=self.path_join(base,fname+'_audio_only.wav') 
        out_vid_fp=self.path_join(base,fname+'_vid_only.webm') 
            
        if do_audio:
            out_audio_fp=self.extract_sound_from_vid(vid_fp=vid_fp,timestamps=timestamps,out_fp=out_audio_fp)
            
        if do_video:
            out_video_fp=self.extract_vid_from_vid(vid_fp=vid_fp,timestamps=timestamps,out_fp=out_vid_fp)
                   
        return out_video_fp,out_audio_fp
    
    def extract_sound_from_vid(self,vid_fp,timestamps=None,out_fp=None):
        ffmpeg=[f"{self.ffmpeg_path}ffmpeg",'-y'] # ffmpeg executable  
        if timestamps is None:  
            l=['-i',f'{vid_fp}','-q:a','0','-map','a',f'{out_fp}']
        else:
            l=['-i',f'{vid_fp}','-ss',f'{timestamps[0]}','-t',f'{timestamps[1]}','-q:a','0','-map','a',f'{out_fp}']
        l=ffmpeg + l     
        self.subprocess_run(l=l)
        return out_fp

    def extract_vid_from_vid(self,vid_fp,
                               timestamps=None,
                               out_fp=None):
        
        out_fp=self.torch_cut_vid(vid_fp=vid_fp,st_flt=0,en_flt=0,out_fp=out_fp)    # pytorch is faster than ffmpeg
        return out_fp
        
        ffmpeg=[f"{self.ffmpeg_path}ffmpeg",'-y'] # ffmpeg executable  
        if timestamps is None:
            l=['-i',f'{vid_fp}','-q:v','0','-map','v',f'{out_fp}']    
        else:
            l=['-i',f'{vid_fp}','-ss',f'{timestamps[0]}','-t',f'{timestamps[1]}','-q:v','0','-map','v',f'{out_fp}']
        l=ffmpeg + l     
        self.subprocess_run(l=l)
        return out_fp

    # adds background to speech  - essentialy overlays two audios 
    def overlay_audios(self,background_fp,speech_fp,out_fp,background_volume=0.2):
        ffmpeg=[f"{self.ffmpeg_path}ffmpeg",'-y'] # ffmpeg executable  
        audio_len=self.get_vid_len(background_fp)
        vid_len=self.get_vid_len(speech_fp)
        if audio_len<=vid_len: # maybe i should make background audio longer here 
            print('background audio is shorter than video')

        l =ffmpeg + ['-i',f'{background_fp}'
                     ,'-i',f'{speech_fp}'
                     ,'-filter_complex'
                     ,f'[0:0]volume={background_volume}[a];[1:0]volume=1[b];[a][b]amix=inputs=2:duration=1', 
                     f'{out_fp}' ]
        self.subprocess_run(l)
        return out_fp
        
    # overlays audio and video 
    def overlay_audio_and_video(self,vid_fp,audio_fp,out_fp,vid_offset=0,audio_offset=0):
        vid_len=self.get_vid_len(vid_fp=vid_fp)                     # get vid len 
        tmp_audio_fp=self.path_join(audio_fp,'tmp.wav',swap=True)   # make tmp audio of same len as vid 
        tmp_audio_fp=self.torch_cut_audio(audio_fp=audio_fp,out_fp=tmp_audio_fp,st_flt=0,dur_flt=vid_len)
        ffmpeg=[f"{self.ffmpeg_path}ffmpeg",'-y'] # ffmpeg executable  
        l=['-itsoffset',f'{vid_offset}'
           ,'-i',vid_fp
            ,'-itsoffset',f'{audio_offset}'
           ,'-i',audio_fp
           ,'-c:v','copy','-map','0:v','-map','1:a',f'{out_fp}']
        l=ffmpeg + l 
        self.subprocess_run(l)
        return out_fp
        
    # combines streams together     
    def concat_streams(self,fps : list,out_fp):
        ffmpeg=[f"{self.ffmpeg_path}ffmpeg"] # ffmpeg executable  
        mylist_fp=self.path_join(self.root_dir,'mylist.txt')
        with open(mylist_fp,'w') as f:
            for fp in fps:
                s=f"file \'{fp}\'" +'\n'
                f.write(s)
        l =ffmpeg + ['-f','concat','-safe','0','-i',f'{mylist_fp}','-y','-c','copy',f'{out_fp}' ]
        self.subprocess_run(l)
        return out_fp
        
    # returns video length in seconds 
    def get_ffmpeg(self,vid_fp,key='bitrate'):
        pass # ffmpeg -i input.mp4 -f null 
        ffmpeg=[f"{self.ffmpeg_path}ffprobe"] # ffmpeg executable  
        l=['-i',f'{vid_fp}'
           ,'-show_format' ]
        l=ffmpeg+l
        out=self.subprocess_run(l)
        for line in out.splitlines():
            if key in line:
                d=line.split('=')
                return np.float(d[1])
        return None 
        
# cuts video to pieces of N length     
    def chopify_video(self,vid_fp,out_dir,N=2,title='',ext='webm'):
        vid_len=self.get_vid_len(vid_fp=vid_fp)  # get vid len 
        cnt = int( vid_len // N  )               # get cnt of files   
        tses=[]
        floats=[]
        for i in range(cnt):                     # for each file 
            st_ts=self.flt_to_ts(i*N)            # calculate tses 
            en_ts=self.flt_to_ts((i+1)*N)
            ts=[st_ts,en_ts]                     # save them 
            tses.append(ts)
            floats.append([i*N,(i+1)*N])
        tses.append([en_ts, self.flt_to_ts(vid_len) ]) # add more tses 
        floats.append( [floats[-1][1],vid_len] )
        for no,ts in enumerate(floats):                   # chop stuff 
            out_fp=self.path_join(out_dir,f'{title}_part_{no}.{ext}')

            self.torch_cut_vid(vid_fp=vid_fp,st_flt=ts[0],en_flt=ts[1],out_fp=out_fp)
            #self.cut_vid_to_timestamps(vid_fp=vid_fp,out_fp=out_fp,timestamps=ts)
        return 
    
    # cuts video to specific timestamps 
    def chopify_to_timestamps(self,vid_fp,out_dir,timestamps=[0,10,20,50],title='',ext='webm'): 
        if timestamps!=sorted(timestamps):
            print('warning your timestamps rae not sorted!')
        tses=[]
        floats=[]
        out_fps=[]
        for no in range(0,len(timestamps),2):
            st=timestamps[no]
            en=timestamps[no+1]
            print(st,en)
            out_fp=self.path_join(out_dir,f'{title}_part_{no}_{st}_{en}.{ext}')
            self.torch_cut_vid(vid_fp=vid_fp,st_flt=st,en_flt=en,out_fp=out_fp)
            out_fps.append(out_fp)
        return out_fps
            
        

        
