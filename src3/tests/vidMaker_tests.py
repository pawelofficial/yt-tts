import sys
import os.path
import json 
import time 
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import unittest


from  vidMaker import vidMaker
from Utils import Utils
import logging

class TestvidMaker(unittest.TestCase):
    def __init__(self):
#    def setUp(self):
        self.utils = Utils()
        self.vm = vidMaker(self.utils)

    def test_tmp_dir(self):
        self.vm.tmp_dir='tests_tmp_dir'
        
    def test_media_fp(self):
        self.vm.media_fp='foo'


    def test_cut_vid_ffmpeg(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        self.vm.media_fp= 'vm_test_input_vid.webm'#  'vm_test_input_vid.webm'
        
        out_fp = self.vm.utils.path_join('tests','tests_outputs','cut_vid_ffmpeg.webm')
        #start_time = time.time()
        out=self.vm.cut_vid_ffmpeg(vid_fp=self.vm.media_fp,out_fp=out_fp,prc=0.5)
        #print(f' cutting took {time.time()-start_time}' )
        print(out )


    def test_cut_vid_moviepy(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        self.vm.media_fp= 'vm_test_input_vid.webm'#  'vm_test_input_vid.webm'
        
        out_fp = self.vm.utils.path_join('tests','tests_outputs','cut_vid_ffmpeg.webm')
        #start_time = time.time()
        out=self.vm.cut_vid_moviepy(vid_fp=self.vm.media_fp,out_fp=out_fp,prc=0.5)
        #print(f' cutting took {time.time()-start_time}' )
        #print(out )


    def test_cut_vid(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        self.vm.media_fp= 'big_vid.webm'#  'vm_test_input_vid.webm'
        
        out_dir_fp = self.vm.utils.path_join('tests','tests_outputs')
        out=self.vm.cut_media(isvideo=True,output_dir_fp=out_dir_fp,prc=0.5)
        print(out )
        
    def test_cut_audio(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        self.vm.media_fp='vm_test_input_audio.wav'
        
        out_dir_fp = self.vm.utils.path_join('tests','tests_outputs')
        self.vm.cut_media(isaudio=True,output_dir_fp=out_dir_fp)

    def test_slowdown_vid_ending(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        self.vm.media_fp='vm_test_slowdown_vid_ending2.webm'
        self.vm.media_fp='THEY_DISCOVERED_ADVANCE_TINY_HUMANS_LIVING_IN_A_FRIDGE.webm'
        
        out_dir_fp = self.vm.utils.path_join('tests','tests_outputs')
        self.vm.slowdown_vid_ending(output_dir_fp=out_dir_fp)

    def test_add_silence(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        self.vm.media_fp='vm_test_input_audio.wav'
        out_dir_fp = self.vm.utils.path_join('tests','tests_outputs')
        self.vm.add_pause_to_audio(output_dir_fp=out_dir_fp)

    def test_add_background_to_audio(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        self.vm.media_fp='vm_test_speech.wav'
        out_dir_fp = self.vm.utils.path_join('tests','tests_outputs')
        background_fname='test_input_background.wav'
        self.vm.add_background_to_audio(output_dir_fp=out_dir_fp,
                                        background_fname=background_fname)
        
    def test_concat_audios(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        fp1=self.vm.utils.path_join(self.vm.tmp_dir,'vm_test_speech.wav')
        fp2=self.vm.utils.path_join(self.vm.tmp_dir,'vm_test_input_audio.wav')
        audio_fps=[fp1,fp2]
        self.vm.concat_audios(audios_fps=audio_fps,output_fname='concat_audio_test.wav')
        
    def test_concat_ffmpeg(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        fp1=self.vm.utils.path_join(self.vm.tmp_dir,'vm_test_speech.wav')
        fp2=self.vm.utils.path_join(self.vm.tmp_dir,'vm_test_input_audio.wav')
        audio_fps=[fp1,fp2]
        self.vm.concat_streams_ffmpg(fps=audio_fps,output_fname='concat_streams_ffmpeg.wav')
        
    def test_concat_audio_video_ffmpeg(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        fp1=self.vm.utils.path_join(self.vm.tmp_dir,'vm_test_speech.wav')
        fp2=self.vm.utils.path_join(self.vm.tmp_dir,'freeze_vid_input2.webm')
        self.vm.concat_audio_and_video(audio_fp=fp1,vid_fp=fp2,output_fname='movie3.webm',tmp_dir=self.vm.tmp_dir)
        
        
    def test_freeze_frames_linearly(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        vids_dir=self.vm.utils.path_join(self.vm.tmp_dir,'vids')
        f='THEY_DISCOVERED_ADVANCE_TINY_HUMANS_LIVING_IN_A_FRIDGE.webm'
        f='freeze_vid_input2.webm'
        fp1=self.vm.utils.path_join(self.vm.tmp_dir,f)
        self.vm.media_fp=fp1
        out_fp=self.vm.utils.path_join('tests','tests_outputs','freeze_frames_lin2.webm')
        tmp_dir=self.vm.utils.path_join('tests','tests_inputs','freeze_dir')


        #self.vm.cut_media(st_flt=0,en_flt=30,isvideo=True,output_fname='freeze_vid_input2.webm')
        #freezed_fp=self.vm.freeze_frames_linearly(vid_fp=fp1
        #                               ,output_fname='freeze_vids_output.webm'
        #                               ,tmp_dir_fp=vids_dir)
        #
        out=self.vm.freeze_frames_linearly2(vid_fp=self.vm.media_fp
                                        ,out_fp=out_fp
                                        ,tmp_dir_fp=tmp_dir
                                        ,N=7,nsec=1)
        
        print(out)
        
        
    def test_concat_vids(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        fp1=self.vm.utils.path_join(self.vm.tmp_dir,'vm_test_input_vid.webm')
        fp2=self.vm.utils.path_join(self.vm.tmp_dir,'vm_test_input_vid.webm')
        vids_fps=[fp1,fp2]
        self.vm.concat_vids(vids_fps=vids_fps,output_fname='concat_vids_test.webm',
                            add_pause_sec=1)
        

if __name__ == '__main__':
    tm=time.time()
    t=TestvidMaker()
    t.test_freeze_frames_linearly()
    print(f'time: {time.time()-tm}')
#    t.test_add_silence
#    t.test_tmp_dir()
#    t.test_media_fp()
#    t.test_slowdown_vid_ending()
#    t.test_cut_vid()
#    t.test_cut_audio()
    

#