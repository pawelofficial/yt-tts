import os 
import json 
import pandas as pd 
import numpy as np 
import torchvision
import re 
import torchaudio
import torch 
import random

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
                  , output_dir_fp = None, output_fname = None):
        if output_dir_fp is None: 
            output_dir_fp = self.tmp_dir
        if output_fname is None: 
            st=str(st_flt).replace('.','')
            en=str(en_flt).replace('.','')
            fname_suffix=f'__cut_{st}_{en}'
            _,meta=self.utils.path_join(self.media_fp,meta=True)                            # to do output to specific dir rather than tmp dir 
            output_fname= meta['fname'].replace('.',f'{fname_suffix}.')
        self.output_fp=self.utils.path_join(output_dir_fp,output_fname)
        
        if isaudio and isvideo:
            print('cant do that')
            return 
        if isvideo:
            vid,audio,info=torchvision.io.read_video(self.media_fp)
            vclip = vid[int(st_flt * info['video_fps']):int(en_flt * info['video_fps'])]
            torchvision.io.write_video(filename=self.output_fp
                                       ,video_array=vclip
                                       ,fps=info['video_fps']
                                        ,video_codec='libvpx'
                                       )
        if isaudio:
            waveform, rate_of_sample = torchaudio.load(self.media_fp)
            trimmed_waveform = waveform[:, int(st_flt *rate_of_sample):int(en_flt * rate_of_sample)]
            torchaudio.save(self.output_fp, trimmed_waveform, rate_of_sample)
        
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


    
    # extracts sound from video 
    def _extract_sound_from_vid(self):
        l=['-i',f'{self.media_fp}','-q:a','0','-map','a',f'{self.out_fp}']
        l=self._ffmpeg + l     
        self.subprocess_run(l=l)

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
#    utils=Utils.Utils()
#    vm=vidMaker(utils)
#    vm.tmp_dir='vm_tmp_dir'

    
    
    


