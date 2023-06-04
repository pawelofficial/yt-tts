

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


def ytd_wf(vm_,url_,lang='en',tmp_dir_name='aaaa'
           ,punctuate=True 
           ,download_vid=True
           ,divide=False
           ,convert=True
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
        ytd.vid_fp=ytd.utils.path_join(ytd.tmp_dir,'short.mov')
        
    if convert:
        ytd.vid_fp=ytd.convert_vid(vid_fp=ytd.vid_fp,tgt_format='mov')
    else:
        ytd.vid_fp=ytd.utils.path_join(ytd.tmp_dir,'Company_Accidentally_Turns_29999_Out_of_30000_Patients_Into_Zombies_During_a_Clinical_Trial.mov')
        
    if divide or True:
        vm_.tmp_dir=ytd.tmp_dir
        half=int(ytd.utils.get_media_len(vid_fp)*2/3)
        out_list=vm_.cut_vid_recurrence(vid_fp=ytd.vid_fp,duration=half,out_dir_fp=ytd.tmp_dir)
        ytd.vid_fp=out_list[0]
        print(out_list)


        
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
    N =int (audio_len-vid_len)                      # no of secs to freeze  
    duration=60                                     # duration of chunk 
    freezes_added=int(vid_len/duration) *5          # 5 freezes per chunk 
    if N>10 and freeze_frames :
        print('freezing frames')
        out_fp=vm.utils.path_join(vm.tmp_dir,f'{ytd.vid_title}_freezed_linearly.webm')
        
        vid_fp=vm.wrapper_freeze_frames_linearly2(vid_fp=ytd.vid_fp
                                    ,out_fp=out_fp
                                    ,tmp_dir_fp=vm.tmp_dir
                                    ,freezes_added=freezes_added
                                    ,nsec=1,duration=duration)
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
  
    
#    urls=['https://www.youtube.com/watch?v=rUByu33vIRs&t=1s&ab_channel=MovieRecaps'
#          ,'https://www.youtube.com/watch?v=HO9ndOtTlW4&ab_channel=MovieRecaps'
#          ,'https://www.youtube.com/watch?v=pPNwpr8tNMg&t=16s&ab_channel=MovieRecaps'
#          ]
    #urls=['https://www.youtube.com/watch?v=2VWzdIYKwmc&ab_channel=LiftingVault']
    for url_ in urls:
        tm=time.time()
        ytd=ytd_wf(vm_=vm_(utils()), url_=url_,lang='en')
        at=tts_wf(ytd=ytd)
        vm_wf(ytd=ytd,at=at)
        winsound.MessageBeep()
        print(f'time: {time.time()-tm}')
        exit(1)
        
        