import sys
import os.path
import json 
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import unittest

from  azureTTS import azureTTS
from Utils import Utils
import logging

class TestAzureTTS(unittest.TestCase):
    def __init__(self):
#    def setUp(self):
        self.utils = Utils()
        self.azure_tts = azureTTS(self.utils)
        self.azure_tts.config='azure.json'

    def test_tmp_dir(self):
        self.azure_tts.tmp_dir = "test_dir"
        expected_dir = self.utils.path_join('tmp','test_dir')
        self.assertEqual(self.azure_tts.tmp_dir, expected_dir)

    def test_logger(self):
        self.azure_tts.logger = "test_logger"
        expected_logger_name = "test_logger"
        self.assertIsInstance(self.azure_tts.logger, logging.Logger)
        self.assertEqual(self.azure_tts.logger.name, expected_logger_name)
        
    def test_config(self):
        self.azure_tts.config = "azure"
        expected_config=self.utils.path_join('secrets','azure.json')
        expected_config=json.load(open(expected_config))
        self.assertDictEqual(self.azure_tts.config,expected_config)

    def test_lang(self):
        self.azure_tts.lang="pl"
        def f():
            self.azure_tts.lang = "foo"  # checks if incorrect lang throws a key error 
        self.assertRaises(KeyError,f)
        
    def test_xml_txt(self):
        self.xml_txt='foo bar'

    def test_tts_df(self):
        fp=self.utils.path_join('tests','tests_inputs','tts_df.csv')
        df=self.utils.read_df(fp=fp)
        self.azure_tts.config='azure.json'
        self.azure_tts.lang='en'
        self.azure_tts.tmp_dir=self.utils.path_join('tests','tests_outputs')
        self.azure_tts.tts_from_df(df=df)
        
    def test_tts_from_df_smart(self):
        fp=self.utils.path_join('tests','tests_inputs','tts_df.csv')
        df=self.utils.read_df(fp=fp)
        self.azure_tts.config='azure.json'
        self.azure_tts.lang='en'
        self.azure_tts.tmp_dir=self.utils.path_join('tests','tests_outputs')
        self.azure_tts.tts_from_df(df=df)

    def test_tts(self):
        self.azure_tts.config='azure.json'
        self.azure_tts.lang='en'
        self.azure_tts.tmp_dir=self.utils.path_join('tests','tests_outputs')
        self.azure_tts.tts(s='hello world i am a test text !')  
    
    def test_tts_Ratio(self):
        s="i'd like to clarify my position on gold for both my longer term subscribers but especially for my newer subscribers i get lots of questions and comments regarding the price action in dollars in the recent past or predictions of the price action in dollars in the near-term future this implies that there is an easy and reliable way to predict the gold price while i do think that over the span of five or more years there are tools that can be used to more or less make accurately reasonable predictions i think that such efforts are dangerous because they can lead us to believe that there are times when we should not hold any gold at all it's akin to thinking that because you're a good driver you shouldn't carry auto insurance honestly i think if we in this community are to do ourselves a service it will be to understand how the truly wealthy of the world view this medal sure there are wealthy people who speculate in gold but the truly wealthy don't own it because they think that it will double in price next year they own it because they acknowledge to"
        tgt_dur="62.88"
        
    
    def test_translate_df(self):
        fp=self.utils.path_join('tests','tests_inputs','subs_df_en_short.csv')
        subs_df=self.utils.read_df(fp=fp)
        df=self.azure_tts.translate_df(df=subs_df,text_column='txt',tgt_langs=['fr','pl','de'])
        print(df)
        #out_dir=self.utils.path_join('tests','tests_outputs')
        #self.azure_tts.utils.dump_df(df=subs_df,fp=out_dir,name='subs_df_pl')
        
        
    def test_translate_string(self):
        s='hello world, how are you?'
        d=self.azure_tts.translate(s=s,text_column='txt')




if __name__ == '__main__':
#    utils=Utils()
#    a=azureTTS(utils=utils)
    t=TestAzureTTS()
    t.test_tts_from_df_smart()
#    t.test_translate_df()
#    unittest.main()
#