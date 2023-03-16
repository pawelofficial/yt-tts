import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import pytest 
import vid_maker as vm 

import ytd 
import utils as ut
import azure_tts as a 
# to run tests cd to this dir \src\tests
#  issue  $ pytest in terminal 
#  issue $ pytest::test_my_method to run specific test  
#  issue $ pytest -m <marker> to issu markers 




if __name__=='__main__':
    i=a.azure_tts()

    speech_fp=i.path_join('tests','tests_inputs','samples_csharp_sharedcontent_console_whatstheweatherlike.mp3')
    speech_fp=i.path_join('tests','tests_inputs','azure_speech_to_text.wav')
    i.stt(speech_fp=speech_fp)


