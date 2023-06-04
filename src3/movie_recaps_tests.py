

from Utils import Utils as utils
from ytURL import ytURL as url
from ytDownloader import ytDownloader as  ytd_ 
from azureTTS import azureTTS as atts_
from vidMaker import vidMaker as vm_ 
import time 
import datetime 
import winsound
import pandas as pd 

def download_vids():
    pass


def ytd_wf(url_,lang='en',tmp_dir_name=None
           ,punctuate=True
           ,download_vid=True
           ,download_subs=True
           ,use_hardcoded_values=False
           ):
    ytd=ytd_(utils(), url())
    if tmp_dir_name is not None:
        ytd.tmp_dir=tmp_dir_name                                                # knob 1 
    else:
        tmp_dir_name=f'{ytd.utils.get_cur_ts()}'
        ytd.tmp_dir=tmp_dir_name
    ytd.url=url_
    if download_vid:
        vid_fp=ytd.download_vid()
    if download_subs:
        ytd.download_subs(lang=lang)
        ytd.parse_json3_to_df()
        ytd.concat_on_time(N=300)  
    if punctuate:
        ytd.punctuate_df(input_col='txt',output_col='txt')
    if use_hardcoded_values:
        ytd.subs_df=ytd.utils.read_df(fp=ytd.utils.path_join(ytd.tmp_dir,'subs_df.csv'))  # subs_df 
        ytd.vid_fp=ytd.utils.path_join(ytd.tmp_dir,'True_Story__From_a_Homeless_Living_in_Public_Toilet_to_a_Wall_Street_Millionairewebm.webm')
        
#    half_df=ytd.subs_df[:len(ytd.subs_df)//2]
#    double_df=pd.concat([ytd.subs_df, ytd.subs_df])
#    ytd.subs_df=double_df
    ytd.vid_fp=ytd.convert_vid(vid_fp=ytd.vid_fp,tgt_format='mov')
    ytd.add_string_to_df()
    ytd.utils.dump_df(df=ytd.subs_df,fp=ytd.tmp_dir,name='subs_df')
    return ytd 
    
def tts_wf(ytd
           ,translate=True
           ,read_hardcoded_values=False
           ):
    at=atts_(utils())
    at.lang='pl'
    at.config='azure.json'
    at.tmp_dir=ytd.utils.path_join(ytd.tmp_dir,'audios')
    if translate:
        at.translate_df(df=ytd.subs_df, text_column='txt',tgt_langs=['pl'])
        at.tts_from_df (df=ytd.subs_df,colname='txt_pl')
        at.utils.dump_df(df=at.tts_df,fp=ytd.tmp_dir,name='tts_df')
    if read_hardcoded_values:
        at.tts_df=ytd.utils.read_df(fp=ytd.utils.path_join(ytd.tmp_dir,'tts_df.csv'))
    return at 
    
    
def vm_wf(ytd,at,
          freeze_frames = True 
          ):
    vm=vm_(utils())
    vm.tmp_dir=vm.utils.path_join(ytd.tmp_dir,'videos')
    
    combined_audio_fp=vm.concat_audios(audios_fps=at.tts_df['wav_fp'].tolist(), output_fname='combined.wav')
    audio_len=vm.get_media_len(combined_audio_fp)
    vid_len=vm.get_media_len(ytd.vid_fp)
    vid_fp=ytd.vid_fp
    N =int (audio_len-vid_len  ) 

    if N>10 and freeze_frames :
        
        print('freezing frames')
        freeze_nsec=abs(N//5*5) 
        print(freeze_nsec)
        out_fp=vm.utils.path_join(vm.tmp_dir,f'{ytd.vid_title}_freezed_linearly.webm')
        
        vid_fp=vm.wrapper_freeze_frames_linearly2(vid_fp=ytd.vid_fp
                                    ,out_fp=out_fp
                                    ,tmp_dir_fp=vm.tmp_dir
                                    ,n_chunks=4
                                    ,N=freeze_nsec,nsec=1,duration=120)
    if not freeze_frames:
        vid_fp=vm.utils.path_join(vm.tmp_dir,f'freezed_chunks_concat.webm')
    
    audio_out_fp=vm.utils.path_join(vm.tmp_dir,f'audio_matched_exactly.wav')
    print(combined_audio_fp)
    print(vid_fp)
    combined_audio_matched,_=vm.match_audio_len_to_video_exactly(audio_fp=combined_audio_fp,vid_fp=vid_fp,audio_out_fp=audio_out_fp)
    print('exactly', vm.get_media_len(combined_audio_matched))
    print('vid', vm.get_media_len(vid_fp))
    print('audio', vm.get_media_len(combined_audio_fp))
    vm.concat_audio_and_video(audio_fp=combined_audio_matched,vid_fp=vid_fp,output_fname=f'{ytd.vid_title}_{ytd.utils.get_cur_ts()}_movie.{vm.format}',tmp_dir=ytd.tmp_dir)

if __name__=='__main__':
    urls=['https://www.youtube.com/watch?v=HO9ndOtTlW4&ab_channel=MovieRecaps']
    urls=['https://www.youtube.com/watch?v=9nEDbbJVlkM&ab_channel=LiftingVault']
    urls=['https://www.youtube.com/watch?v=svYL6yb426Q&ab_channel=LiftingVault']  # lang='en'
#    urls=['https://www.youtube.com/watch?v=ESwGjkxToiU&ab_channel=MovieRecaps']  # lang='en-en
#    urls=['https://www.youtube.com/watch?v=oRw-EdPsako&ab_channel=BarkeyReviewsMovies']
#    urls=['https://www.youtube.com/watch?v=ESwGjkxToiU&ab_channel=MovieRecaps']
  
    

    urls=[urls[0]]
    for url_ in urls:
        tm=time.time()
        #if 1:
        ytd=ytd_wf(url_=url_,lang='en')
        at=tts_wf(ytd=ytd)
        vm_wf(ytd=ytd,at=at)
        winsound.MessageBeep()
        print(f'time: {time.time()-tm}')
            
        exit(1)
        tm=time.time()
        ytd=ytd_(utils(), url())
        ytd.tmp_dir=f'aa_movie_recaps_tests_{ ytd.utils.get_cur_ts()}'
        #ytd.tmp_dir=ytd.utils.path_join('tmp','tests')
        ytd.url=url_
        id_fp=ytd.download_vid()
        ytd.download_subs(lang='en-en')
        ytd.parse_json3_to_df()
        ytd.concat_on_time(N=300)  
        if 0:
            ytd.punctuate_df(input_col='txt',output_col='txt')
        else:
            print('reading from file ')
            ytd.subs_df=ytd.utils.read_df(fp=ytd.utils.path_join(ytd.tmp_dir,f'{ytd.vid_title}.csv'))  
        
        ytd.utils.dump_df(df=ytd.subs_df,fp=ytd.tmp_dir,name=ytd.vid_title)
        print(f'downloading and parsing : {time.time()-tm}')
        
    # make audio files 
        tm=time.time()
        at=atts_(utils())
        at.lang='pl'
        at.config='azure.json'
        at.tmp_dir=at.utils.path_join(ytd.tmp_dir,'audios')
        #at.translate_df(df=ytd.subs_df, text_column='txt',tgt_langs=['pl'])
        #at.tts_from_df (df=ytd.subs_df,colname='txt_pl')
        #at.utils.dump_df(df=at.tts_df,fp=ytd.tmp_dir,name='tts_df')

        # to delete 
        # tts_df=ytd.utils.read_df(fp=ytd.tmp_dir,name='tts_df.csv') 
        # vid_fp=ytd.utils.path_join(ytd.tmp_dir,'LBMA_Storage_and_the_Gold_to_Silver_Ratiowebm.webm')
        tts_df=at.tts_df
        vid_fp=ytd.vid_fp
        print(f'making audio files : {time.time()-tm}')
        
    # make video 
        tm=time.time()
        vm=vm_(utils())
        vm.tmp_dir=vm.utils.path_join(ytd.tmp_dir,'videos')
        combined_audio=vm.concat_audios(audios_fps=tts_df['wav_fp'].tolist(), output_fname='combined.wav')
        
        
        print(f'making a vid 1 : {time.time()-tm}')
        
        tm=time.time()
        titles_ns=[]
        audio_len=vm.get_media_len(combined_audio)
        vid_len=vm.get_media_len(vid_fp)
        N =int (audio_len-vid_len  ) 
        #input('wait')
        if N>10 and False :
            print('freezing frames')
            freeze_nsec=abs(N//5*5) 
            print(freeze_nsec)
            out_fp=vm.utils.path_join(vm.tmp_dir,f'{ytd.vid_title}_freezed_linearly.webm')
            
            vid_fp=vm.wrapper_freeze_frames_linearly2(vid_fp=vid_fp
                                        ,out_fp=out_fp
                                        ,tmp_dir_fp=vm.tmp_dir
                                        ,n_chunks=10
                                        ,N=freeze_nsec,nsec=1)
            
        vid_fp=ytd.utils.path_join(ytd.tmp_dir,'freezed_chunks_concat.webm')
        combined_audio_fp=vm.utils.path_join(vm.tmp_dir,'combined_matched.wav')
        
        combined_audio_matched,_=vm.match_audio_len_to_video_exactly(audio_fp=combined_audio,vid_fp=vid_fp,audio_out_fp=combined_audio_fp)
        
        titles_ns.append( f'{ytd.vid_title} :  {N} rozjazd' )
        movies_dir=vm.utils.path_join('tmp','movies2')
        #vm.wrapper_freeze_frames_linearly2(vid_fp=vid_fp,combined_audio_fp=combined_audio_matched,N=N,vid_out_fp=f'{ytd.vid_title}_movie.webm',tmp_dir=movies_dir)
        vm.concat_audio_and_video(audio_fp=combined_audio_matched,vid_fp=vid_fp,output_fname=f'{ytd.vid_title}_{ytd.utils.get_cur_ts()}_movie.webm',tmp_dir=movies_dir)        
        print(ytd.vid_title,' finished')
        print(f'making a vid 2: {time.time()-tm}')
        
    for t in titles_ns:
        print(t)