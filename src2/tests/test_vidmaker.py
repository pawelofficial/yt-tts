import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import pytest 
import vid_maker as vm 

import ytd 
import utils as ut
# to run tests cd to this dir \src\tests
#  issue  $ pytest in terminal 
#  issue $ pytest::test_my_method to run specific test  
#  issue $ pytest -m <marker> to issu markers 


def set_vm():
    i=vm.vid_maker()
    return i 

@pytest.mark.ytd
def test_get_vid_len():
    """ tests whether invoking wizard works and variables are initiated  """
    i=set_vm()
    vid_fp=i.path_join('tests','tests_inputs','vm_test_input_vid2.webm')
    audio_fp=i.path_join('tests','tests_inputs','test_input_speech.wav')
    print(i.get_vid_len(vid_fp=vid_fp))
    print(i.get_vid_len(vid_fp=audio_fp))
    return 

def test_extract_sound_from_vid():
    i=set_vm()
    vid_fp=i.path_join('tests','tests_inputs','vm_test_input_vid.webm')
    out_dir=i.path_join('tests','tests_outputs')
    i.split_sound_and_video(vid_fp=vid_fp,out_dir=out_dir,do_audio=True,do_video=False)

def test_extract_vid_from_vid():
    i=set_vm()
    vid_fp=i.path_join('tests','tests_inputs','vm_test_input_vid.webm')
    out_dir=i.path_join('tests','tests_outputs')
    i.split_sound_and_video(vid_fp=vid_fp,out_dir=out_dir,do_audio=False,do_video=True)

def test_cut_vid():
    i=set_vm()
    vid_fp=i.path_join('tests','tests_inputs','vm_test_input_vid.webm')
    out_fp=i.path_join('tests','tests_outputs','vm_test_output_cut_vid.webm')
    i.torch_cut_vid(vid_fp=vid_fp,out_fp=out_fp,st_flt=8,en_flt=30)
    
def test_cut_audio():
    i=set_vm()
    audio_fp=i.path_join('tests','tests_inputs','test_input_background.wav')
    audio_fp=i.path_join('tests','tests_inputs','test_input_speech.wav')
    out_fp=i.path_join('tests','tests_outputs','vm_test_output_cut_audio.wav')
    i.torch_cut_audio(audio_fp=audio_fp,out_fp=out_fp,st_flt=0,en_flt=30)

def test_boomerangize():
    i=set_vm()
    vid_fp=i.path_join('tests','tests_inputs','vm_test_input_boomerang.webm')
    out_fp=i.path_join('tests','tests_outputs','vm_test_output_boomerang.webm')
    i.torch_boomerang(vid_fp=vid_fp,out_fp=out_fp)
    
def test_overlay_audios():
    i=set_vm()
    background_fp=i.path_join('tests','tests_inputs','test_input_background.wav')
    speech_fp=i.path_join('tests','tests_inputs','test_input_speech.wav')
    out_fp=i.path_join('tests','tests_outputs','vm_test_output_add_background.wav')
    i.overlay_audios(background_fp=background_fp,speech_fp=speech_fp,out_fp=out_fp)
    
def test_overlay_audio_and_video():
    audio_fp=i.path_join('tests','tests_inputs','test_input_background.wav')
    vid_fp=i.path_join('tests','tests_inputs','fiuty12345.webm')
    out_fp=i.path_join('tests','tests_outputs','vm_test_output_overlay_audio_and_video.webm')
    i.overlay_audio_and_video(vid_fp=vid_fp,audio_fp=audio_fp,out_fp=out_fp)
    
def test_chopify_video():
    vid_fp=i.path_join('tests','tests_inputs','vm_test_input_vid.webm')
    out_dir=i.path_join('tests','tests_outputs')
    i.chopify_video(vid_fp=vid_fp,out_dir=out_dir,N=10)
    
def test_chopify_to_timestamps():
    vid_fp=i.path_join('tests','tests_inputs','vm_test_input_vid.webm')
    out_dir=i.path_join('tests','tests_outputs')
    timestamps=[0,10,20,50]
    i.chopify_to_timestamps(vid_fp=vid_fp,out_dir=out_dir,timestamps=timestamps)
    
def test_concat_streams():
    fp0=i.path_join('tests','tests_inputs','_part_0.webm')
    fp1=i.path_join('tests','tests_inputs','_part_1.webm')
    fp2=i.path_join('tests','tests_inputs','_part_2.webm')
    out_fp=i.path_join('tests','tests_outputs','test_concat_streams.webm')
    i.concat_streams(fps=[fp0,fp1,fp2],out_fp=out_fp)
    
def test_workflow(background_fp = None, speech_fp = None, yt_raw_fp=None):
    if background_fp is None:
        background_fp=i.path_join('tests','tests_inputs','test_input_background.wav')       # get background  from outside 
    if speech_fp is None: 
        speech_fp=i.path_join('tests','tests_inputs','test_speech.wav')                     # get speech file from outside 
    if yt_raw_fp is None:
        yt_raw_fp=i.path_join('tests','tests_inputs','vm_test_input_vid.webm')              # get raw yt vid 
    
    tests_outputs_dir=i.path_join('tests','tests_outputs')
    # 1. split yt video and audio 
    if 1: # takes long time 
        yt_vid_video_fp,yt_vid_audio_fp=i.split_sound_and_video(vid_fp=yt_raw_fp,out_dir=tests_outputs_dir,do_audio=True,do_video=True)
    else:
        yt_vid_video_fp=i.path_join('tests','tests_outputs','vm_test_input_vid.webm')
        yt_vid_audio_fp=i.path_join('tests','tests_outputs','vm_test_input_vid.wav')

    # 2. combine speech and background together towards speech len 
    speech_and_background_fp=i.path_join('tests','tests_outputs','speech_and_background.wav')
    speech_and_background_fp=i.overlay_audios(background_fp=background_fp,speech_fp=speech_fp,out_fp=speech_and_background_fp)
 
    # 3. cut yt vid to some lengths 
    if 1:
        cut_yt_vid_fp=i.path_join('tests','tests_outputs','cut_yt_vid.webm')
        cut_yt_vid_fp=i.torch_cut_vid(vid_fp=yt_vid_video_fp,out_fp=cut_yt_vid_fp,st_flt=7,dur_flt=10)
    else:
        cut_yt_vid_fp=i.path_join('tests','tests_outputs','cut_yt_vid.webm')
        
    # 4. boomerangize video so it matches speech len  
    if 1:
        boomerang_fp=i.path_join('tests','tests_outputs','boomerang.webm')
        boomerang_fp=i.torch_boomerang(vid_fp=cut_yt_vid_fp,out_fp=boomerang_fp,n=0)
    else:
        boomerang_fp=i.path_join('tests','tests_outputs','boomerang.webm')
    
    #5. concat video further so it matches speech len 
    if 1:
        final_vid_fp=i.path_join('tests','tests_outputs','final_vid.webm')
        tgt_len=i.get_vid_len(speech_fp)
        N= int(tgt_len // (i.get_vid_len(boomerang_fp)) + 1)
        final_vid_fp=i.concat_streams(fps=[boomerang_fp for i in range(N)],out_fp=final_vid_fp )
        background_len=i.get_vid_len(speech_and_background_fp)
        final_vid_fp=i.torch_cut_vid(vid_fp=final_vid_fp,out_fp=final_vid_fp,st_flt=0,en_flt=background_len)
        
    else:
        final_vid_fp=i.path_join('tests','tests_outputs','final_vid.webm')
        
    # 6. concat speech with background and final vid together 
    final_mov_fp=i.path_join('tests','tests_outputs','final_mov.webm')
    final_mov_fp=i.overlay_audio_and_video(vid_fp=final_vid_fp,audio_fp=speech_and_background_fp,out_fp=final_mov_fp)
     
        
if __name__=='__main__':
    i=vm.vid_maker()
    out_dir=i.path_join('tests','tests_outputs')
    i.clear_dir(out_dir)
    if 0:
        test_get_vid_len()
        test_extract_sound_from_vid()
        test_extract_vid_from_vid()
        test_cut_vid()
        test_cut_audio()
        test_extract_sound_from_vid()
        test_extract_vid_from_vid()
        test_boomerangize()
        test_overlay_audios()
        test_overlay_audio_and_video()
        test_chopify_video()
        test_concat_streams()
        
#    test_extract_sound_from_vid()
#    test_workflow()
    test_chopify_to_timestamps()



