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



if __name__ == '__main__':
#    utils=Utils()
#    a=azureTTS(utils=utils)
    t=TestAzureTTS()
    t.test_tts_df()
#    unittest.main()
#