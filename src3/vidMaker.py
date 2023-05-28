import os 
import json 
import pandas as pd 
import numpy as np 
import torchvision
import re 
import torchaudio
import torch 
import random
import pydub 
from moviepy.editor import VideoFileClip, AudioClip
import matplotlib.pyplot as plt 
import time 
import Utils 
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# all methods should accept input_fname or input_fp
#       input_fname defaults to tmp_dir for fp 
# all methods should accept output_fnames or output_fps
#       output_fnames default to tmp_dir for fp 

# all methods should have input_fp and optionally output_fp(s) / output_fnames
#   if output_fp is not provided output_fnames use tmp_dir 

class vidMaker:
    def __init__(self,utils):               
        self.utils=utils
        self._tmp_dir = None       # tmp directory      
        self._logger  = None       # logger 

        
        self._media_fp = None 
        self.logger='vidMaker_logger'
        self.output_fp = None      # outp  ut file 
        self._ffmpeg_path="C:\\ffmpeg\\bin\\"        
        

    
    # cuts media to timestamps whether a video or an audio 
    def cut_media(self,st_flt=0,en_flt = 3, fname_suffix = None
                  , isaudio=False,isvideo = False
                  , output_dir_fp = None, output_fname = None,**kwargs):
        if output_dir_fp is None: 
            output_dir_fp = self.tmp_dir
        if output_fname is None: 
            st=str(st_flt).replace('.','')
            en=str(en_flt).replace('.','')
            fname_suffix=f'__cut_{st}_{en}'
            _,meta=self.utils.path_join(self.media_fp,meta=True)                            # to do output to specific dir rather than tmp dir 
            output_fname= meta['fname'].replace('.',f'{fname_suffix}.')
        self.output_fp=self.utils.path_join(output_dir_fp,output_fname)
        
        prc=kwargs.get('prc',None)
        if prc is not None:
            media_len=self.get_media_len(fp=self.media_fp)
            st_flt=0 
            en_flt=media_len*prc
        
        if isaudio and isvideo:
            print('cant do that')
            return 
        if isvideo:
            print('cutting video')
            vid,audio,info=torchvision.io.read_video(self.media_fp,start_pts=st_flt,end_pts=en_flt,pts_unit='sec')
            torchvision.io.write_video(filename=self.output_fp
                                       ,video_array=vid
                                       ,fps=info['video_fps']
                                        ,video_codec='libvpx-vp9'
                                        ,options={
                                                    '-crf': '0',  # Adjust the Constant Rate Factor (CRF) for quality vs. size trade-off
                                                    '-b:v': '1M',  # Specify the video bitrate (adjust as needed)
                                                    '-quality':'best',
                                                    '-speed': '0',
                                        }
                                       )
        if isaudio:
            waveform, rate_of_sample = torchaudio.load(self.media_fp)
            trimmed_waveform = waveform[:, int(st_flt *rate_of_sample):int(en_flt * rate_of_sample)]
            torchaudio.save(self.output_fp, trimmed_waveform, rate_of_sample)
            
        return self.output_fp
        
    def slowdown_tensor_ending(self,vid_t,nsec=2,fps=None):
        dur=vid_t.shape[0]/fps
        print(f'input tensor dur {dur, fps }')
        vid_duration=vid_t.shape[0]/fps # vid duration in secs 
        clip_start_index=int ( (vid_duration-nsec)*fps )  # start of slowdown clip 
        clip=vid_t[clip_start_index:]    
        blank_tensor=clip[0:1]
        for n in range(len(clip)):
            #print(blank_tensor.shape)
            c=clip[n:n+1]
            blank_tensor=torch.cat((blank_tensor,c,c),dim=0)
        out_tensor=torch.cat((vid_t[:clip_start_index],blank_tensor),dim=0)
        dur=out_tensor.shape[0]/fps
        print(f'tensor duration {dur}')
        return out_tensor
    
    # slows down last n seconds of vid in the worst possible way 
    def slowdown_vid_ending(self, nsec=2,output_dir_fp = None, output_fname = None):
        if output_dir_fp is None: 
            output_dir_fp = self.tmp_dir
        if output_fname is None: 
            _,meta=self.utils.path_join(self.media_fp,meta=True) 
            st=str(nsec).replace('.','')
            fname_suffix=f'__slowed_{st}_'
            output_fname= meta['fname'].replace('.',f'{fname_suffix}.')
            
        self.output_fp=self.utils.path_join(output_dir_fp,output_fname)
        vid,audio,info=torchvision.io.read_video(self.media_fp)
        vid_duration=len(vid)/info['video_fps']
        clip_start_index=int ( (vid_duration-nsec)*info['video_fps'] ) 
        clip=vid[clip_start_index:]        
        blank_tensor=clip[0:1]
        for n in range(len(clip)):
            c=clip[n:n+1]
            # would be nice to add effect here 
            #c[:,:,:,0] +=random.randint(0,5)
            #c[:,:,:,1] +=random.randint(0,5)
            #c[:,:,:,2] +=random.randint(0,5)
            blank_tensor=torch.cat((blank_tensor,c,c),dim=0)
        out_tensor=torch.cat((vid[:clip_start_index],blank_tensor),dim=0)
        torchvision.io.write_video(filename=self.output_fp
                                       ,video_array=out_tensor
                                       ,fps=info['video_fps']
                                        ,video_codec='libvpx'
                                       )

    # adds pause to the audio of specific duration in seconds      
    def add_pause_to_audio(self,nsec=2, output_dir_fp = None, output_fname = None):
        if output_dir_fp is None: 
            output_dir_fp = self.tmp_dir
        if output_fname is None: 
            _,meta=self.utils.path_join(self.media_fp,meta=True) 
            st=str(nsec).replace('.','')
            fname_suffix=f'__paused_{st}_'
            output_fname= meta['fname'].replace('.',f'{fname_suffix}.')    
        self.output_fp=self.utils.path_join(output_dir_fp,output_fname)
        waveform, rate_of_sample = torchaudio.load(self.media_fp)
        clip=torch.zeros(2,rate_of_sample*nsec) # silent clip
        waveform_with_silence = torch.cat([waveform,clip], dim=1)
        torchaudio.save(self.output_fp, waveform_with_silence, rate_of_sample)
        
    # adds background to media_fp 
    def add_background_to_audio(self,background_fp = None, background_fname=None, 
                                output_dir_fp = None, output_fname = None
                                ,background_volume=0.2):
        if output_dir_fp is None: 
            output_dir_fp = self.tmp_dir        
        if background_fp is None:
            background_fp=self.utils.path_join(self.tmp_dir,background_fname)
        if output_fname is None: 
            _,meta=self.utils.path_join(self.media_fp,meta=True) 
            fname_suffix=f'__with_bckg_'
            output_fname= meta['fname'].replace('.',f'{fname_suffix}.')    
            
        self.output_fp=self.utils.path_join(output_dir_fp,output_fname)
    
    
        ffmpeg=[f"{self._ffmpeg_path}ffmpeg",'-y'] # ffmpeg executable  
        l =ffmpeg + ['-i',f'{background_fp}'
                     ,'-i',f'{self.media_fp}'
                     ,'-filter_complex'
                     ,f'[0:0]volume={background_volume}[a];[1:0]volume=1[b];[a][b]amix=inputs=2:duration=1', 
                     f'{self.output_fp}' ]
        self.utils.subprocess_run(l)


    def cut_vid_moviepy(self,vid_fp,out_fp,st_flt=0,en_flt=10,**kwargs):
        prc=kwargs.get('prc',None)
        if prc is not None:
            media_len=self.get_media_len(fp=self.media_fp)
            st_flt=0 
            en_flt=media_len*prc
        ffmpeg_extract_subclip(vid_fp, st_flt, en_flt, targetname=out_fp)
        return out_fp

    def cut_vid_ffmpeg(self,vid_fp,out_fp,st_flt=0,en_flt=10,**kwargs):
        prc=kwargs.get('prc',None)
        if prc is not None:
            media_len=self.get_media_len(fp=self.media_fp)
            st_flt=0 
            en_flt=media_len*prc
        
        timestamps=[st_flt,en_flt] 
        ffmpeg=[f"{self._ffmpeg_path}ffmpeg",'-y'] # ffmpeg executable  
        if timestamps is None:
            l=['-i',f'{vid_fp}','-q:v','0','-map','v',f'{out_fp}']    
        else:
            l=['-i',f'{vid_fp}','-ss',f'{timestamps[0]}','-t',f'{timestamps[1]}','-q:v','0','-map','v',f'{out_fp}']
        l=ffmpeg + l     
        self.utils.subprocess_run(l)
        return out_fp

    def cut_vid_pydub(self,st_flt,en_flt,vid_fp,out_fp):
        pass
        

    # get media len in seconds 
    def get_media_len(self,fp):
        try:
            audio_len=len(pydub.AudioSegment.from_file(fp))/1000
            return audio_len
        except Exception as err:
            clip = VideoFileClip(fp)           
            return clip.duration

    # concats audio together 
    def concat_audios(self,audios_fps : list =[],output_dir_fp = None, output_fname = None
                      ,add_pause_sec=0):
        if output_dir_fp is None: 
            output_dir_fp = self.tmp_dir
        if output_fname is None: 
            output_fname='concat_audio.wav'   
            
        self.output_fp=self.utils.path_join(output_dir_fp,output_fname)
        ws=[]
        for fp in audios_fps:
            waveform, rate_of_sample = torchaudio.load(fp)
            ws.append(waveform)
            if add_pause_sec>0:
                    clip=torch.zeros(2,rate_of_sample*add_pause_sec) # silent clip
                    ws.append(clip)

            
            
        t=torch.cat(tuple(ws),dim=1)   
        torchaudio.save(self.output_fp, t, rate_of_sample)
        return self.output_fp
    
    # concats vids together 
    def concat_vids(self,vids_fps: list=[],output_dir_fp = None, output_fname = None
                    ,add_pause_sec=0):
                    
        if output_dir_fp is None: 
            output_dir_fp = self.tmp_dir
        if output_fname is None: 
            output_fname='concat_vid.webm'  
        self.output_fp=self.utils.path_join(output_dir_fp,output_fname)
        ws=[]
        for fp in vids_fps:
            vid,audio,info=torchvision.io.read_video(fp)
            ws.append(vid)
            if add_pause_sec>0:
                n=int(add_pause_sec*info['video_fps'])
                clip=torch.ones(n,vid.shape[1],vid.shape[2],vid.shape[3])*256
                ws.append(clip)
        t=torch.cat(tuple(ws),dim=0)   
        torchvision.io.write_video(filename=self.output_fp
                                       ,video_array=t
                                       ,fps=info['video_fps']
                                        ,video_codec='libvpx'
                                       )
        return self.output_fp
        
        
    def dump_tensor(self,t,fname,dir_fp,fps=None):
        if dir_fp is None:
            dir_fp=self.tmp_dir
        output_fp=self.utils.path_join(dir_fp,fname)

        torchvision.io.write_video(filename=output_fp
                                       ,video_array=t
                                       ,fps=fps
                                        ,video_codec='libvpx'
                                       )
        return output_fp


    def concat_audio_and_video(self,audio_fp,vid_fp,output_fname='movie.webm',tmp_dir=None,
                               vid_offset=0,audio_offset=0):
        if tmp_dir is None:
            tmp_dir=self.tmp_dir
        ffmpeg=[f"{self._ffmpeg_path}ffmpeg"] # ffmpeg executable          
        out_fp=self.utils.path_join(tmp_dir,output_fname)
        l=['-itsoffset',f'{vid_offset}'
           ,'-i',vid_fp
            ,'-itsoffset',f'{audio_offset}'
           ,'-i',audio_fp
           ,'-c:v','copy','-map','0:v','-map','1:a',f'{out_fp}']
        
        l=ffmpeg+l
        self.utils.subprocess_run(l)
        return out_fp
        
    
    def concat_streams_ffmpg(self,fps : list,output_fname='concated_streams.webm',tmp_dir=None):
        if tmp_dir is None:
            tmp_dir=self.tmp_dir
        ffmpeg=[f"{self._ffmpeg_path}ffmpeg"] # ffmpeg executable  
        mylist_fp,meta=self.utils.path_join(tmp_dir,'mylist.txt',meta=True)
        if meta['exists']==False:
            with open(mylist_fp,'w') as f:
                f.write('')
        out_fp=self.utils.path_join(tmp_dir,output_fname)
        with open(mylist_fp,'w') as f:
            for fp in fps:
                s=f"file \'{fp}\'" +'\n'
                f.write(s)
        l =ffmpeg + ['-y','-f','concat','-safe','0','-i',f'{mylist_fp}','-y','-c','copy',f'{out_fp}' ]
        self.utils.subprocess_run(l)
        return out_fp
        
    def extract_vid_from_vid(self,vid_fp,
                               st_flt=0,
                               en_flt=-1
                               ,output_dir_fp = None, output_fname = None):
        
        if output_dir_fp is None: 
            output_dir_fp = self.tmp_dir
        if output_fname is None: 
            output_fname='extract_vid_from_vid.webm' 
        self.output_fp=self.utils.path_join(output_dir_fp,output_fname)
        if en_flt==-1:
            en_flt=self.get_media_len(vid_fp) 
        self.output_fp=self.utils.path_join(output_dir_fp,output_fname)
        
        ffmpeg=[f"{self._ffmpeg_path}ffmpeg",'-y'] # ffmpeg executable  
        if en_flt  == self.get_media_len(vid_fp) :
            l=['-i',f'{vid_fp}','-q:v','0','-map','v',f'{self.output_fp}']    
        else:
            l=['-i',f'{vid_fp}','-ss',f'{st_flt}','-t',f'{en_flt}','-q:v','0','-map','v',f'{self.output_fp}']
        l=ffmpeg + l     
        self.utils.subprocess_run(l=l)
        return self.output_fp
        
    # duplicates frames of audio tensor to match the total len to the video 
    def match_audio_len_to_video_exactly(self,vid_fp,audio_fp,audio_out_fp):
        def stretch_audio(audio, stretch_factor):
            """Stretches an audio signal by duplicating frames."""
            num_frames = audio.shape[-1]
            expanded_num_frames = int(num_frames * stretch_factor)
            indices = (torch.arange(expanded_num_frames) / stretch_factor).long()
            stretched_audio = audio[..., indices]
            return stretched_audio
        # match audio len to video len exactly  
        vid_len=self.get_media_len(fp=vid_fp)
        audio_len=self.get_media_len(fp=audio_fp)

        waveform, rate_of_sample = torchaudio.load(audio_fp)
        
        stretch_factor = vid_len / audio_len
        if abs(1-stretch_factor)>0.05:
            print('watch out buster, your stretch factor is pretty big!')
        
        stretched_waveform = stretch_audio(waveform, stretch_factor)
    
        torchaudio.save(audio_out_fp, stretched_waveform,rate_of_sample)

        new_len=self.get_media_len(fp=audio_out_fp)
        return audio_out_fp ,(vid_len, audio_len, new_len) 
        
    def wrapper_freeze_frames_linearly2(self,vid_fp,out_fp,nsec=1,N=10,tmp_dir=None):
        # first splits up original video to smaller chunks so i dont run out of memory in pytorch 
        pass 
        
        
    def freeze_frames_linearly2(self,vid_fp,out_fp,nsec=1,N=10,tmp_dir_fp=None):
        vid_len=self.get_media_len(fp=vid_fp)
        fps=self.utils.get_vid_fps(vid_fp=vid_fp)
        vid_nframes=int(vid_len*fps)
        start_frame=0
        frame_interval=(vid_nframes//(N))
        
        if tmp_dir_fp is None:
            tmp_dir_fp=self.tmp_dir
        
        dumped_fps=[]
        k=0
        for i in range(frame_interval,vid_nframes+frame_interval,frame_interval):
            start_sec=start_frame/fps 
            end_sec=int(start_sec+frame_interval/fps+1)
            
            clip, audio_chunk, info = torchvision.io.read_video(vid_fp, start_pts=start_sec, end_pts=end_sec,pts_unit='sec')
            print(f'clip dur ', clip.shape[0]/fps, fps  )
            clip=self.slowdown_tensor_ending(vid_t=clip[:frame_interval],nsec=nsec,fps=fps)
            
            fp=self.dump_tensor(t=clip,fname=f'{str(k)}_vid_.webm',dir_fp=tmp_dir_fp,fps=fps)
            dumped_fps.append(fp)
            start_frame=i
            k+=1
        out=self.concat_streams_ffmpg(fps=dumped_fps,output_fname=out_fp,tmp_dir=tmp_dir_fp)
        print(out)

    # adds pauses ( freeze frames ) linearly N times for nsec each time 
    def freeze_frames_linearly(self,vid_fp = None ,output_dir_fp = None, output_fname = None
                    ,nsec=1,N=10,tmp_dir_fp=None):    
                        
        start_time = time.time()
        if output_dir_fp is None: 
            output_dir_fp = self.tmp_dir
        if output_fname is None: 
            output_fname='vid_freezed.webm' 
        self.output_fp=self.utils.path_join(output_dir_fp,output_fname)

            
        vid_len=self.get_media_len(fp=vid_fp)         # duration in sec 
        fps=self.utils.get_vid_fps(vid_fp=vid_fp)     # fps 
        vid_nframes=int(vid_len*fps)
        nn=int(fps*nsec)
        print(vid_nframes)
        start_frame=0
        frame_interval=(vid_nframes//(N))
        ws=[]
        k=0
        dumped_fps=[]
#        for i in range(frame_interval,vid_nframes,frame_interval):
#            start_sec=start_frame/fps 
#            print(start_sec,start_sec+frame_interval/fps,start_sec+frame_interval/fps+nsec*(k+1))
#            k+=1
#            start_frame=i
#        exit(1)
#        input('wait')
        k=0
        for i in range(frame_interval,vid_nframes+frame_interval,frame_interval):
            start_sec=start_frame/fps 
            end_sec=int(start_sec+frame_interval/fps+1)
            print(start_sec,end_sec)
#            print(start_frame,start_frame+frame_interval)

            clip, audio_chunk, info = torchvision.io.read_video(vid_fp, start_pts=start_sec, end_pts=end_sec,pts_unit='sec')
            print(f'clip dur ', clip.shape[0]/fps, fps  )
#            clip=vid[:frame_interval,:,:,:]
            #print(f'foobar {vid.shape}')
            #print(vid.shape,info)
            
            clip=self.slowdown_tensor_ending(vid_t=clip[:frame_interval],nsec=nsec,fps=fps)
            frame=clip[-1,:,:,:]
#            freeze_vid=torch.ones(nn,vid.shape[1],vid.shape[2],vid.shape[3])*frame
#            ws.append(clip)
#            ws.append(freeze_vid)
            
            fp=self.dump_tensor(t=clip,fname=f'{str(k)}_vid_.webm',dir_fp=tmp_dir_fp,fps=fps)
            dumped_fps.append(fp)
#            fp=self.dump_tensor(t=freeze_vid,fname=f'{str(k)}_freeze_.webm',dir_fp=tmp_dir_fp,fps=fps)
#            dumped_fps.append(fp)
            start_frame=i
            k+=1
            if k>3:
                pass
#                break
#                pass # break
                
            
        print(dumped_fps)
        out_fp=self.concat_streams_ffmpg(fps=dumped_fps,tmp_dir=tmp_dir_fp)
        return out_fp
        exit(1)
        NN=0
        for w in ws:
            NN+=w.shape[0]
        out_t=torch.zeros(NN,vid.shape[1],vid.shape[2],vid.shape[3])
        for w in ws:
            out_t[:w.shape[0]]=w
            print(out_t.shape)
        t=out_t
                   
#        t=ws[0]
#        for i in range(1,len(ws)):
#            t=torch.cat((t,ws[i]),dim=0 )   
#        
        torchvision.io.write_video(filename=self.output_fp
                                       ,video_array=t
                                       ,fps=info['video_fps']
                                        ,video_codec='libvpx'
                                       )
        
    
    
    # extracts sound from video 
    def _extract_sound_from_vid(self,vid_fp=None, out_fp=None):
        ffmpeg=[f"{self._ffmpeg_path}ffmpeg",'-y'] # ffmpeg executable  
        
        if out_fp is None:
            out_fp=self.out_fp
        if vid_fp is None:
            vid_fp=self.media_fp
        l=['-i',f'{vid_fp}','-q:a','0','-map','a',f'{out_fp}']
        l=ffmpeg + l     
        self.utils.subprocess_run(l=l)

    @property 
    def media_fp(self):
        return self._media_fp
    @media_fp.setter
    def media_fp(self,fname):
        self._media_fp,meta=self.utils.path_join(self.tmp_dir,fname,meta=True)
        if not meta['exists']: # if filed does not exist log a warning 
            print(f'warning - media fp {self._media_fp}\n does not exist')
            self.utils.log_variable(logger=self.logger,msg=f'media fp does not exist',media_fp=self._media_fp,lvl='warning')    
    @property 
    def tmp_dir(self):
        return self._tmp_dir
    @tmp_dir.setter 
    def tmp_dir(self,dir):
        self._tmp_dir = self.utils.path_join('tmp',dir)
        self.utils.make_dir(fp=self._tmp_dir) 
    @property 
    def logger(self):
        return self._logger    
    @logger.setter 
    def logger(self,nm='azureTTS_logger'):
        self._logger = self.utils.setup_logger(name=nm,log_file=f'{nm}.log')
    


if __name__=='__main__':
    pass
    utils=Utils.Utils()
    vm=vidMaker(utils)
    vm.tmp_dir='2023052012'
    output_dir_fp=vm.utils.path_join(vm.tmp_dir,'output')    
    input_vid='indiana.webm'


    vm.media_fp=vm.utils.path_join(vm.tmp_dir,input_vid)
    timestamp_to_float = lambda timestamp: sum(float(x) * 60 ** i for i, x in enumerate(reversed(timestamp.split(':'))))
    scenes={
        '01_into':['01:57.50','01:59.25'],
        '02_memcen':['01:59.25','02:00.00'],
        '03_nothing':['02:00.00','02:05.00'],
        '04_miecz':['02:05.80','02:08.00'],
        '':['02:08.60','02:13.43']
            }
    scenes_flt={}
    for key, timestamps in scenes.items():
        scenes_flt[key] = list(map(timestamp_to_float, timestamps))
    
    for k,v in scenes_flt.items():
        title=f'{k}.webm'
        st=v[0]
        en=v[1] 
        x=vm.cut_media(st_flt=st,en_flt=en,output_fname=title,isvideo=True)
        print(x)
    
    
    


