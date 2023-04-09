import os 
import json 
import pandas as pd 
import numpy as np 
import re 

import Utils 
import ytURL
import azure.cognitiveservices.speech as sdk

class azureTTS:
    def __init__(self,utils):               
        self.utils=utils
        self.ytURL   = ytURL       # attribute for youtube url with some other stuff behind it 
        self._url    = None        # url provided by user 
        self._tmp_dir = None       # tmp directory      
        self._logger  = None       # logger 
        self._config = None      # config for azure 
        self._xml_txt   = None                  # xml string 
        self._lang = None               # lang, must be present in lang_names 
        self._txt = None                 # txt in xml 
        self._rate=1.05                  # rate in xml
        #self.logger='azureTTS_logger'
        
        # dummy text if you need a dummy text for something 
        self.dummy_texts={'pl':'cześć, jestem głosem azure, w czym mogę Ci pomóc ?'
                         ,'en':'hello i am azure text to speech, what do you want me to do?'
                         ,'de':'Hallo, ich bin Azure Text-to-Speech, was soll ich tun?'}

        # voices available in azure 
        self.lang_names={'pl':'pl-PL-MarekNeural'
                           ,'de':'de-AT-JonasNeural' # https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=tts
                           ,'en':'en-CA-LiamNeural'} #
        
        self.logger='azureTTS_logger'
        self.speech_config = None 
        self.audio_config = None 
        self.speech_synthesizer = None 
        self.wav_fp = None                      # set by _setup_audio_config, output wav file 
        self.tts_df = None                      # set by tts_df 
        self.out_dir_fp = None 
        
        
    # sets up speech config 
    def _setup_speech_config(self):
        self.speech_config = sdk.SpeechConfig(subscription=self.config['key1'], region=self.config['region'])
        self.speech_config.speech_synthesis_voice_name=self.lang_names[self.lang]
        
    # sets up audio config and wav_fp if it's for tts 
    def _setup_audio_config(self,talk = False, tts = False, fname = None ):
        if self.out_dir_fp is None:
            self.out_dir_fp = self.tmp_dir
        
        if talk:
            self.audio_config = sdk.audio.AudioOutputConfig(use_default_speaker=True) 
        elif tts: 
            fp = self.utils.path_join(self.out_dir_fp,fname.replace('.wav','')+'.wav' )
            self.audio_config = sdk.audio.AudioOutputConfig(filename=fp) 
            self.wav_fp = fp 
             
    # sets up speech synthesizer 
    def _setup_speech_synthesizer(self):
        self.speech_synthesizer = sdk.SpeechSynthesizer(speech_config=self.speech_config,
                                                        audio_config=self.audio_config)
        
    # logs synthesis results     
    def check_synthesis_result(self,speech_synthesis_result):
        error_details = None 
        cancellation_details = None 
        reason  = speech_synthesis_result.reason
        if reason == sdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            if cancellation_details.reason == sdk.CancellationReason.Error:
                error_details=cancellation_details.error_details
        
        self.utils.log_variable(logger=self.logger,msg='speech synthesis results'
                                ,reason = reason
                                ,cancellation_details = cancellation_details
                                ,error_details = error_details
                                ,wav_fp = self.wav_fp)


    # talks 
    def talk(self,s = None):
        if self.speech_config is None:
            self._setup_speech_config()
        if self.audio_config is None: 
            self._setup_audio_config(talk = True )
        if self.speech_synthesizer is None:
            self._setup_speech_synthesizer()
        if s is not None:
            self.txt = s # update self.txt as well as xml_txt 
        if s is None:
            self.txt = self.dummy_texts[self.lang]
            
        speech_synthesis_result = self.speech_synthesizer.speak_ssml(self.xml_txt)
        self.check_synthesis_result(speech_synthesis_result=speech_synthesis_result)
        
    # does tts 
    def tts(self,fname='test', s = None):
        if self.out_dir_fp is None: 
            self.out_dir_fp = self.tmp_dir
        
        if s is not None:
            self.txt = s # update self.txt as well as xml_txt 
        if self.speech_config is None:
            self._setup_speech_config()                         # refresh speech config if it's none  
        self._setup_audio_config(tts = True ,fname=fname)       # refresh audio config to refresh output file 
        self._setup_speech_synthesizer()                        # refresh synthesizer sience audio config was refreshed 
        speech_synthesis_result = self.speech_synthesizer.speak_ssml(self.xml_txt)
        self.check_synthesis_result(speech_synthesis_result=speech_synthesis_result)
        

    # loops through df column and dumps .wav files 
    def tts_from_df(self,df,colname='txt',N=999):
        for no,row in df.iterrows():
            s=row['txt']
            print(s)
            fname=self.utils.hash(s)+'.wav'
            self.tts(fname=fname,s=s)
            df.loc[no,'fname']=fname
            df.loc[no,'wav_fp']=self.wav_fp # os.path.abspath(self.wav_fp)
            df.loc[no,'wav_len']=self.utils.get_media_len(media_fp = self.wav_fp)
            if no >= N : # speed things up with N parameter 
                print('done')
                break
        self.tts_df=df

    @property 
    def rate(self):
        return self._rate
    @rate.setter 
    def rate(self,f):
        self.rate=f
        self.xml_txt = self.xml_txt # update xml_txt with new rate 
    @property 
    def txt(self):
        return self._txt
    @txt.setter 
    def txt(self,s):
        self._txt=s
        self.xml_txt = self.xml_txt # update xml_txt with new txt 
    @property 
    def lang(self):
        return self._lang 
    @lang.setter 
    def lang(self,s):
        if s not in self.lang_names.keys():
            raise KeyError(f' {s} not defined in lang_names ')
        self._lang=s
        self.xml_txt=self.xml_txt # update xml_txt with new lang 
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
    @property 
    def config(self):
        return self._config
    @config.setter
    def config(self,fname):
        fp=self.utils.path_join('secrets',fname.replace('.json','')+'.json')
        self._config = json.load(open(fp))
    @property 
    def xml_txt(self):
        return self._xml_txt
    @xml_txt.setter
    def xml_txt(self,lang = None ,rate = None ,txt = None ):
        s=f"""
            <speak version="1.0" xmlns="https://www.w3.org/2001/10/synthesis" xml:lang="en-US">
                <voice name="{self.lang_names[self.lang]}">
                    <prosody rate="{self.rate}"> 
                        {self.txt}
                    </prosody>
                </voice>
            </speak>
            """
        self._xml_txt=s
    


if __name__=='__main__':
    utils=Utils.Utils()
    a=azureTTS(utils)
    a.config='azure.json'
    a.lang='en'
    a.tmp_dir=a.utils.path_join('tests','tests_outputs')
    fp=a.utils.path_join('tests','tests_inputs','tts_df.csv')
    df=a.utils.read_df(fp=fp)
    a.tts_from_df(df=df)

    
    
    


