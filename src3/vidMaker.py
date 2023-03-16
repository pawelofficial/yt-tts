import os 
import json 
import pandas as pd 
import numpy as np 
import torchvision
import re 
import torchaudio

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
        self.out_fp = None      # output file 
        
        

        
    # cuts media to timestamps whether a video or an audio 
    def cut_media(self,st_flt=0,en_flt = 10, fname_suffix = None, isaudio=False,isvideo = False):
        if self.out_dir_fp is None:
            self.out_dir_fp = self.tmp_dir
        if fname_suffix is None:
            st=str(st_flt).replace('.','')
            en=str(en_flt).replace('.','')
            fname_suffix=f'__cut_{st}_{en}'
            
        _,meta=self.utils.path_join(self.media_fp,meta=True)                            # to do output to specific dir rather than tmp dir 
        out_fp_name= meta['fname'].replace('.',f'{fname_suffix}.')
        out_fp=self.utils.path_join(self.out_dir_fp,out_fp_name)
            
        if isvideo:
            vid,audio,info=torchvision.io.read_video(self.media_fp)
            vclip = vid[int(st_flt * info['video_fps']):int(en_flt * info['video_fps'])]
            torchvision.io.write_video(filename=out_fp
                                       ,video_array=vclip
                                       ,fps=info['video_fps']
                                        ,video_codec='libvpx'
                                       )
        if isaudio:
            waveform, rate_of_sample = torchaudio.load(self.media_fp)
            trimmed_waveform = waveform[:, int(st_flt *rate_of_sample):int(en_flt * rate_of_sample)]
            torchaudio.save(out_fp, trimmed_waveform, rate_of_sample)
        self.out_fp = out_fp
        
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

    
    
    


