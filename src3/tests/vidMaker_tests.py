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

    def test_convert_vid(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        vid_fp=self.vm.utils.path_join('tests','tests_inputs','big_vid_webm.webm')
        print('vconverting')
        out_fp=self.vm.convert_vid(vid_fp=vid_fp)
        print(out_fp)


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
        
        
    def test_extract_sound_from_vid(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        vid_fp=self.vm.utils.path_join(self.vm.tmp_dir,'Russian_Streetlifter_Tests_His_Benchwebm.webm')
        out_fp=self.vm.utils.path_join('tests','tests_inputs','test_match_audio_len_to_vid_audio.wav')
        self.vm._extract_sound_from_vid(vid_fp=vid_fp,out_fp=out_fp)
        
    def test_match_audio_len_to_vid_audio(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        audio_fp=self.vm.utils.path_join(self.vm.tmp_dir,'test_match_audio_len_to_vid_audio_input.wav')
        vid_fp=self.vm.utils.path_join(self.vm.tmp_dir,'test_match_audio_len_to_vid_video.webm')
        out_fp=self.vm.utils.path_join('tests','tests_outputs','test_match_audio_len_to_audio_output.wav')
        fp,_ = self.vm.match_audio_len_to_video_exactly(audio_fp=audio_fp,vid_fp=vid_fp,audio_out_fp=out_fp)
        print(_)
        
        
    def test_freeze_frames_linearly(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        vids_dir=self.vm.utils.path_join(self.vm.tmp_dir,'vids')
        f='THEY_DISCOVERED_ADVANCE_TINY_HUMANS_LIVING_IN_A_FRIDGE.webm'
        f='freeze_frames_linearly_1m_input.mp4'
        fp1=self.vm.utils.path_join(self.vm.tmp_dir,f)
        self.vm.media_fp=fp1
        out_fp=self.vm.utils.path_join('tests','tests_inputs','freeze_dir',f'out_{f}')
        tmp_dir=self.vm.utils.path_join('tests','tests_inputs','freeze_dir')

        out=self.vm.freeze_frames_linearly2(vid_fp=self.vm.media_fp
                                        ,out_fp=out_fp
                                        ,tmp_dir_fp=tmp_dir
                                        ,nsec=2               # duration of each cut 
                                        ,N=6                 # how many cuts 
                                        ,duration=45
                                        )
        
        print(out)
        print(self.vm.utils.get_media_len(fp1))
        print(self.vm.utils.get_media_len(out_fp))
        
        
    def test_concat_vids(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        fp1=self.vm.utils.path_join(self.vm.tmp_dir,'vm_test_input_vid.webm')
        fp2=self.vm.utils.path_join(self.vm.tmp_dir,'vm_test_input_vid.webm')
        vids_fps=[fp1,fp2]
        self.vm.concat_vids(vids_fps=vids_fps,output_fname='concat_vids_test.webm',
                            add_pause_sec=1)
        
    def test_freeze_frames_wrapper(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')        # input vid dir 
        vids_dir=self.vm.utils.path_join('tests','tests_inputs','freeze_dir')  # tmp dir 
        f='freeze_frames_wrapper_input.mov'
        f='freeze_frames_linearly_1m_input.mp4'
        vid_fp=self.vm.utils.path_join(self.vm.tmp_dir,f)                      # input video 
        
        out_fp=self.vm.utils.path_join(vids_dir,f'out_{f}')                     # output video
        tmp_dir=self.vm.utils.path_join('tests','tests_inputs','freeze_dir')
        
        out=self.vm.wrapper_freeze_frames_linearly2(vid_fp=vid_fp
                                        ,out_fp=out_fp
                                        ,tmp_dir_fp=tmp_dir   
                                        ,nsec=5                              # single slowdown len 
                                        ,duration=30                         # duration of a chunk 
                                        ,N=10                                # how many cuts in total 
                                        )
        print(out)
        input('wait')
        
    def test_cut_vid_in_half(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        vids_dir=self.vm.utils.path_join(self.vm.tmp_dir,'vids')
        tmp_dir=self.vm.utils.path_join('tests','tests_inputs','tmp_dir')
        f='freeze_frames_linearly_1m_input.webm'
        
        vid_fp=self.vm.utils.path_join(self.vm.tmp_dir,f)
        out_fp1,out_fp2=self.vm.cut_vid_ffmpeg_in_half(vid_fp=vid_fp,out_dir_fp=tmp_dir)
    
    def test_cut_vid_recurrence(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs','tmp_qual')
        vids_dir=self.vm.utils.path_join('tests','tests_inputs','tmp_qual')
#        self.vm.utils.clear_dir(vids_dir)
        f='input.mp4'
        vid_fp=self.vm.utils.path_join(self.vm.tmp_dir,f)
        out_list=self.vm.cut_vid_recurrence(vid_fp=vid_fp,out_dir_fp=vids_dir,duration=60)
        #self.vm.utils.clear_dir(dir_path=vids_dir,save_fps=out_list)
        self.vm.concat_streams_ffmpg(fps=out_list,output_fname='recurrence_concat.mp4',tmp_dir=vids_dir)
        print(out_list)


    def test_copy_file(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        vids_dir=self.vm.utils.path_join(self.vm.tmp_dir,'vids')
        self.vm.utils.clear_dir(vids_dir)
        tmp_dir=self.vm.utils.path_join('tests','tests_inputs','tmp_dir')
        f='freeze_frames_linearly_2m_input.webm'
        
        input_fp=self.vm.utils.path_join(self.vm.tmp_dir,f)
        output_fp=self.vm.utils.path_join(self.vm.tmp_dir,'copy.webm')
        self.vm.copy_file(input_fp,output_fp)

if __name__ == '__main__':
    tm=time.time()
    t=TestvidMaker()
#    t.test_cut_vid_ffmpeg()
    #t.test_cut_vid_recurrence()
    t.test_freeze_frames_wrapper()
    #test_freeze_frames_linearly
#    t.test_freeze_frames_wrapper()
    print(f'time: {time.time()-tm}')
#    t.test_add_silence
#    t.test_tmp_dir()
#    t.test_media_fp()
#    t.test_slowdown_vid_ending()
#    t.test_cut_vid()
#    t.test_cut_audio()
    

#