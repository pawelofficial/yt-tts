from utils import utils 
import os 
import glob 
import re 
import pandas as pd 
from tabulate import tabulate 
import numpy as np 
import json 
import requests 
import os
import azure.cognitiveservices.speech as speechsdk
import hashlib 
import pydub 
import math 
import datetime
from gtts import gTTS

class azure_tts(utils):
    def __init__(self) -> None:
        super().__init__()
        self.today=datetime.datetime.now().strftime("%Y%m%d")
        self.tmp_dir=self.path_join('tmp',self.today)           # path to tmp dir , /tmp/today
        self.vids_dir=self.path_join(self.tmp_dir,'vids')
        
        self.logger=self.setup_logger(name='azure_tts_logger',log_file='azure_tts_logger.log')
        
        self.resource="tts-mn" # "tts-1"
        
        self.config_json=self.path_join('secrets','azure.json')
        self.config_d=json.load(open(self.config_json))[self.resource]
        self.lambda_hash= lambda s: hashlib.sha256(s.encode()).hexdigest()
        self.lambda_floor = lambda fl,n : math.trunc(fl*10**n)/10**n
        
        self.key1=self.config_d['key1']        
        self.region='westeurope'
        self.vids_fp=self.path_join(self.tmp_dir,'vids')                   # direcotry where to save stuffg 
        
        # dummy texts      
        self.dummy_texts={'pl':'cześć, jestem głosem azure, w czym mogę Ci pomóc ?'
                         ,'en':'hello i am azure text to speechch, what do you want me to do?'
                         ,'de':'Hallo, ich bin Azure Text-to-Speech, was soll ich tun?'}
        
        # dictionary with local names that i like 
        self.localnames={'pl':'Marek'
                           ,'de':'Jonas'
                           ,'en':'Liam'}
        
        # hardcode it or use set_lang 
        
        self.lang='pl'
        self.lang_shortname='pl-PL-MarekNeural'
        self.text=self.dummy_texts[self.lang]
        #self.lang_shortname=self.find_voices(key='LocalName',value=self.localnames[self.lang])[1][0]
        
        self.ssml_fp=self.path_join('tmp','ssml.xml')
        self.ssml_txt='<ssml_txt>'
        self.ssml_rate='<ssml_rate>'
        self.ssml_lang='<ssml_lang>'
        self.ssml_string = open(self.ssml_fp, "r").read().replace(self.ssml_lang,self.lang_shortname)
        self.subs_df=None                   # df with subs to translate 
        self.txt_col='txt'
        self.ffmpeg_path="C:\\ffmpeg\\bin\\"
    
    # sets language to use 
    def set_lang(self,lang):
        self.lang=lang
        self.lang_shortname=self.find_voices(key='LocalName',value=self.localnames[self.lang])[1][0]
        self.text=self.dummy_texts[self.lang]

    # translates df         
    def translate_df(self,subs_df = None, lang = None, col = None):
        subs_df = subs_df if subs_df is not None else self.subs_df 
        lang = lang if lang is not None else self.lang 
        col=col if col is not None else self.txt_col
        audio_fps=[]
        combined_fp=self.path_join('tmp','vids','combined.wav')
        
        for no,row in subs_df.iterrows():
            
            txt=row['txt']
            #print(no,txt)
            hash=self.lambda_hash(txt)
            hash=f'00{no}_'+hash
            fp = self.tts(out_filename=hash,txt=txt)            # dump .wav 
            duration=self.get_vid_len(fp)                       # get it's duration 
            ratio=round(row['dif']/duration,2)**-1              # target duration 
            
            print(no,duration,ratio)
            ratio=np.round(ratio,2)
            
            fp = self.tts(out_filename=hash,txt=txt,ssms=True,rate=ratio)
            duration2=self.get_vid_len(fp)
            target_duration=row['dif']
            print(f'original duration {duration}')
            print(f'target duration   {target_duration}')
            print(f'adjusted  duration {duration2}')
            ratio=1
            
            
            audio_fps.append(fp)
            input('wait')
        
        self.combine_audio(audio_fps=audio_fps,out_fp=combined_fp)

        return 
            
    # combines audios together     
    def combine_audio(self,audio_fps : list,out_fp):
        ffmpeg=[f"{self.ffmpeg_path}ffmpeg"] # ffmpeg executable  
        mylist_fp=self.path_join(self.tmp_dir,'mylist.txt')
        with open(mylist_fp,'w') as f:
            for fp in audio_fps:
                s=f"file \'{fp}\'" +'\n'
                f.write(s)
        
        l =ffmpeg + ['-f','concat','-safe','0','-i',f'{mylist_fp}','-y','-c','copy',f'{out_fp}' ]
        self.subprocess_run(l)
        return 
    
    
    def change_speed(self,vid_fp,ratio=0.5,swap=True,no=''):
        # >ffmpeg -i audio1.mp3 -filter atempo=2.0 out.mp3
        r='r'+str(round(ratio*1,2)).replace('.','')
        out_fp=re.sub('\.',f'_{r}_{no}.',vid_fp)
        l=[f"{self.ffmpeg_path}ffmpeg","-i", vid_fp, "-filter", f"atempo={ratio}",  out_fp]
        out=self.subprocess_run(l)
        if swap: 
            tmp=re.sub('\.',f'_tmp_.',vid_fp)
            os.rename(vid_fp,tmp)
            os.rename(out_fp,vid_fp)
            os.remove(tmp)
            return vid_fp
        return out_fp
    
    # adds pause to the video
    def add_pause(self,vid_fp,duration=0.0,swap = False,prepend=False ):
        if np.round(duration,2)==0.00:
            return vid_fp
        
        from moviepy.audio.io.AudioFileClip import AudioClip
        from moviepy.editor import  AudioFileClip,concatenate_audioclips
        silent_clip = AudioClip(lambda t: 0, duration=duration)
        vid = AudioFileClip(vid_fp)
        if prepend:
            output = concatenate_audioclips([silent_clip,vid])
        else:
            output = concatenate_audioclips([vid,silent_clip])
        if swap:
            output.write_audiofile(vid_fp)
        else:
            vid_fp,_=self.strip_extension(s=vid_fp)
            vid_fp=vid_fp+'_pause_.wav'
            output.write_audiofile(vid_fp)
        
        return vid_fp
            
    # returns length of a video file in seconds 
    # to delete 
    def get_vid_len(self,vid_fp):
        return len(pydub.AudioSegment.from_file(vid_fp))/1000
        
    # read subs to self.subs_df
    def read_df(self,df_name = None , df_fp = None):
        if df_name is not None:
            df_fp=self.path_join(self.tmp_dir,df_name)
        self.subs_df=pd.read_csv(filepath_or_buffer=df_fp,quotechar='"',delimiter='|')
        return self.subs_df.copy(deep=True)
    # azure tts 
    def tts(self,out_filename='test.wav',txt=None,ssms=False,rate=1.0):
        if '.wav' not in out_filename:
            out_filename+='.wav'
        if txt is None :
            txt=self.text
        speech_config = speechsdk.SpeechConfig(subscription=self.key1, region=self.region)
        speech_config.speech_synthesis_voice_name=self.lang_shortname
        fp=self.path_join(self.vids_dir,out_filename)
        audio_config = speechsdk.audio.AudioOutputConfig(filename=fp)  
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        
        ssml_string=self.ssml_string.replace(self.ssml_txt,txt).replace(self.ssml_rate,str(rate))
        speech_synthesis_result = speech_synthesizer.speak_ssml(ssml_string)
               
        self.check_res(speech_synthesis_result,text=txt)
        return fp # returns fp to output 
        
    # local gtts because of azure throttling 
    def gtts(self,out_filename='test.wav',txt=None,ssms=False,rate=1.0):
        lambda_tts = lambda txt: gTTS(txt, lang=self.lang, tld=self.lang)
        tts=lambda_tts(txt=txt)
        tts.slow=False
        fp=self.path_join(self.vids_dir,out_filename)+'.wav'
        tts.save(fp)
        return fp 
        
        
    # talks 
    def talk(self,txt=None,rate=1.5):
        import time 
        if txt is None :
            txt=self.text
            
        speech_config = speechsdk.SpeechConfig(subscription=self.key1, region=self.region)
        speech_config.speech_synthesis_voice_name=self.lang_shortname
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)  
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        ssml_string=self.ssml_string.replace(self.ssml_txt,txt).replace(self.ssml_rate,str(rate))
        speech_synthesis_result = speech_synthesizer.speak_ssml(ssml_string)
        self.check_res(speech_synthesis_result,text=txt)
             
    def check_res(self,speech_synthesis_result,text):
        status = 0
        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            x= "Speech synthesized for text [{}]".format(text)
            status = 1 
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            x= "Speech synthesis canceled: {}".format(cancellation_details.reason)
            
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    x= "Error details: {}".format(cancellation_details.error_details)
                    x += "Did you set the speech resource key and region values?"
            print(f' TTS DIDNT WORK {x}')
            
                    
        self.log_variable(logger=self.logger,msg=f' tts status ',lvl='warning',x=x)
        
        d={'msg':x,'status':status}
        try:
            self.log_variable(logger=self.logger,msg='talk speech synthesis results',
                              audio_data=speech_synthesis_result.audio_data,
                              audio_duration=speech_synthesis_result.audio_duration,
                              cancellation_details=speech_synthesis_result.cancellation_details,
                              reason=speech_synthesis_result.cancellation_details.reason,
                              error_details=speech_synthesis_result.cancellation_details.error_details
                              )
        except:
            self.log_variable(logger=self.logger,msg='didnt log' )
        return d
    # finds available voices by a key 
    def find_voices(self,key='LocaleName',value='polish'):
#        {'Marek': {'Name': 'Microsoft Server Speech Text to Speech Voice (pl-PL, MarekNeural)', 'DisplayName': 'Marek', 'LocalName': 'Marek', 'ShortName': 'pl-PL-MarekNeural', 'Gender': 'Male', 'Locale': 'pl-PL', 'LocaleName': 'Polish (Poland)', 'SampleRateHertz': '48000', 'VoiceType': 'Neural', 'Status': 'GA', 'WordsPerMinute': '128'}}
        # find available voices by key and their value - 
        url='https://westeurope.tts.speech.microsoft.com/cognitiveservices/voices/list'
        headers={'Ocp-Apim-Subscription-Key': self.key1}
        r=requests.get(url,headers=headers)
        local_voices_d={}
        shortnames=[]

        for d in r.json():
            try:
                your_key=d[key].upper()
            except KeyError as er:
                print(f'key {key} not found') 
                print(f'available keys are {d.keys()}')
                print(f'available dict:  {d}')
                return {},[]       
            if value.upper() in d[key].upper():
                local_voices_d[d[key]]=d
                shortnames.append(d['ShortName'])

        if local_voices_d=={}:
            return {},[]
        
        return local_voices_d,shortnames
    
    
    # makes vids from df text and updates df 
    def make_a_vid(self,txt,rate=1):
        self.clear_dir(fp=self.vids_dir)

        hash=f'{self.lambda_hash(s=txt)}_.wav'
        fp=self.tts(out_filename=hash,txt=txt,ssms=True,rate=rate) 
        len=self.get_vid_len(vid_fp=fp)
        return fp,len
        
    # tbd 
    def make_vids(self,df : pd.DataFrame = None):
        self.clear_dir(fp=self.vids_dir)
        if df is None:
            df=self.subs_df
            
        for no,row in df.iterrows():
            txt=row['txt']
            hash=f'{str(no)}_' +self.lambda_hash(s=txt)
            #gtts#fp=self.gtts(out_filename=hash,txt=txt,ssms=True,rate=1.0)
            fp=self.tts(out_filename=hash,txt=txt,ssms=True,rate=1.0)      # wtf azure throttling like 1 request every month 
            #self.talk(txt=txt,rate=1.0)
            duration=self.get_vid_len(vid_fp=fp)
            tgt_duration=row['dif']+row['pause_flt']
            ratio=np.round(duration/tgt_duration,2)
            print(ratio)
            if ratio>1: #gtts#self.change_speed(vid_fp=fp,ratio=ratio,swap=True)
                fp=self.tts(out_filename=hash,txt=txt,ssms=True,rate=ratio)
            else:
                pause=tgt_duration-duration
                self.add_pause(vid_fp=fp,duration=pause,swap=False)
            
            df.loc[no,'vid_fp']=fp
            if no > 1:
                print(df)
        l=df['vid_fp'].to_list()
        out_fp=self.path_join(self.vids_dir,'combined.wav')
        self.combine_audio(audio_fps=l,out_fp=out_fp)
        return duration+pause
        
    # let's try speech to text my friend 
    def stt(self,speech_fp,out_fp=None):
        speech_config = speechsdk.SpeechConfig(subscription=self.key1, region=self.region)
        speech_config.speech_recognition_language="en-US"
        
        audio_config = speechsdk.audio.AudioConfig(filename=speech_fp)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        print(dir(speech_recognizer))
        result = speech_recognizer.start_continuous_recognition()
        done = False 
        #while not done:



if __name__=='__main__':
    a=azure_tts()
    a.set_lang(lang='pl')
    a.read_df(df_name='tts_df.csv')
    a.make_vids()
#    a.talk()
    
    
    exit(1)


def combine():
    a=azure_tts()
    p=a.path_join('tmp','vids')
    files=[]
    for file in os.listdir(p):
        fp=a.path_join('tmp','vids',file)
        files.append(fp)

    out_fp=a.path_join('tmp','vids','combined.wav')
    a.combine_audio(audio_fps=files,out_fp=out_fp)
    exit(1)
    
if __name__=='__main__x':
    a=azure_tts()
    a.set_lang='pl'
    a.clear_tmp('tmp','vids')
    exit(1)
    df_name='agg.csv'
    a.read_df(df_name=df_name)
    a.translate_df()
    exit(1)
    
    print(a.subs_df)
    cdf=a.subs_df
    fp=a.path_join('tmp','translated_df.csv')
    cdf.to_csv(path_or_buf=fp,sep='|',quoting=1)
    

#    x=a.find_voices(locale='english')
#    x=a.find_voices(key='Locale',value='en-ca')
#    print(x)
#    a.wizard()
 #   a.make_file(fname='foo.wav',txt='hello world ! ')
 #   a.make_file(fname='bar.wav',txt='goodbye world!')
   # a.dummy2()