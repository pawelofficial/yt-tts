import sys
import os.path
import json 
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


    def test_cut_vid(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        self.vm.media_fp='vm_test_input_vid.webm'
        
        out_dir_fp = self.vm.utils.path_join('tests','tests_outputs')
        self.vm.cut_media(isvideo=True,output_dir_fp=out_dir_fp)
        
    def test_cut_audio(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        self.vm.media_fp='vm_test_input_audio.wav'
        out_dir_fp = self.vm.utils.path_join('tests','tests_outputs')
        self.vm.cut_media(isaudio=True,output_dir_fp=out_dir_fp)

    def test_slowdown_vid_ending(self):
        self.vm.tmp_dir=self.vm.utils.path_join('tests','tests_inputs')
        self.vm.media_fp='vm_test_slowdown_vid_ending2.webm'
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

if __name__ == '__main__':
    t=TestvidMaker()
    t.test_add_background_to_audio()
#    t.test_add_silence
#    t.test_tmp_dir()
#    t.test_media_fp()
#    t.test_slowdown_vid_ending()
#    t.test_cut_vid()
#    t.test_cut_audio()
    

#