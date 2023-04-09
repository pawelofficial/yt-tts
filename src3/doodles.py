

from Utils import Utils as utils
from ytURL import ytURL as url
from ytDownloader import ytDownloader as  ytd 
from azureTTS import azureTTS as atts
from vidMaker import vidMaker as vm 
import time 
import datetime 


def prep_offline(ytd,atts,vm,url,tmp_dirname,mov):                 
    ytd.tmp_dir=tmp_dirname # '2023040217' # '2023040215' # '2023040211' # '2023040210'                                    # ytd tmp dir 
    atts.tmp_dir=atts.utils.path_join(ytd.tmp_dir,'audios')   # azure tmp dir
    vm.tmp_dir=vm.utils.path_join(ytd.tmp_dir,'videos')
    ytd.url=url

    f=mov
    ytd.vid_fp=ytd.utils.path_join(ytd.tmp_dir,f)
    ytd.subs_df=ytd.utils.path_join(ytd.tmp_dir,'subs_df.csv')

    audio_fp=ytd.utils.path_join(atts.tmp_dir,'chunks_combined.wav')
    audio_len=vm.get_media_len(audio_fp)
    
    ytd_vid_len=vm.get_media_len(ytd.vid_fp)   
    nsec=2
    N =int ( (audio_len-ytd_vid_len  ) / nsec ) # 15.5 
    
    print(nsec)
    print(f'audio len {audio_len}')
    print(f'ytd vid len {ytd_vid_len}')
    print(f'no of splits {N}')

    if N<=0:
        fp=ytd.cut_media(st_flt=0,en_flt=audio_len-5)
        print('dupa!')
        exit(1)
    
    vids_dir=ytd.utils.path_join(ytd.tmp_dir,'videos')
    vid_fp=vm.freeze_frames_linearly(vid_fp=ytd.vid_fp,output_dir_fp=ytd.tmp_dir,output_fname='test'
                              ,nsec=nsec,N=N,tmp_dir_fp=vids_dir)
    
    print(audio_fp)
    print(vid_fp)
    print(ytd.tmp_dir)

    vm.concat_audio_and_video(audio_fp=audio_fp,vid_fp=vid_fp,output_fname='movie10s.webm',tmp_dir=ytd.tmp_dir)




    # download some subs and make some wavs 
def prep(ytd,atts,vm,url,tmp_dirname,mov):                                         
    ytd.tmp_dir=tmp_dirname # '2023040217' # '2023040215' # '2023040211' # '2023040210'                                    # ytd tmp dir 
    atts.tmp_dir=atts.utils.path_join(ytd.tmp_dir,'audios')   # azure tmp dir
    vm.tmp_dir=vm.utils.path_join(ytd.tmp_dir,'videos')
    ytd.url=url
    if 0:
        ytd.download_vid()
        isavailable, langs_d= ytd.check_available_subs_langs(lang='pl-en')
        print(isavailable)
        ytd.download_subs(lang='pl-en')   
    else:
        f=mov
        ytd.vid_fp=ytd.utils.path_join(ytd.tmp_dir,f)
        ytd.subs_df=ytd.utils.path_join(ytd.tmp_dir,'subs_df.csv')

    
    
                   


    ytd.parse_json3_to_df()                                 # parse subs to df 
    chunks_d=ytd.get_chunks_of_subs()
    ytd.concat_on_time(N=60)                                # concat on 30s chunks 
    ytd.utils.dump_df(df=ytd.subs_df,fp=ytd.tmp_dir, name='subs_df_chunks')   # dump subs_df
#    chunks_fps=[]
#    for k,v in chunks_d.items():
#        st_str=str(v['st_flt']).replace('.','-')
#        en_str=str(v['en_flt']).replace('.','-')
#        fname=f'chunk_{k}_{st_str}_{en_str}'
#        s=v['chunk'].replace(',','')
#        atts.tts(fname=fname,s=v['chunk'])
#        fp=atts.wav_fp
#        chunks_fps.append(fp)
#        print(k)
#
#    audio_fp=vm.concat_audios(audios_fps=chunks_fps
#                     ,output_dir_fp=atts.tmp_dir
#                     ,output_fname='chunks_combined.wav')
#    
#    audio_len=vm.get_media_len(audio_fp)
    audio_fp=ytd.utils.path_join(atts.tmp_dir,'chunks_combined.wav')
    audio_len=vm.get_media_len(audio_fp)
    
    ytd_vid_len=vm.get_media_len(ytd.vid_fp)   
    nsec=2
    N =int ( (audio_len-ytd_vid_len  ) / nsec ) # 15.5 
    
    print(nsec)
    print(f'audio len {audio_len}')
    print(f'ytd vid len {ytd_vid_len}')
    print(f'no of splits {N}')

    if N<=0:
        fp=ytd.cut_media(st_flt=0,en_flt=audio_len-5)
        print('dupa!')
        exit(1)
    
    return 
    vids_dir=ytd.utils.path_join(ytd.tmp_dir,'videos')
    vid_fp=vm.freeze_frames_linearly(vid_fp=ytd.vid_fp,output_dir_fp=ytd.tmp_dir,output_fname='test'
                              ,nsec=nsec,N=N,tmp_dir_fp=vids_dir)
    
    print(audio_fp)
    print(vid_fp)
    print(ytd.tmp_dir)

    vm.concat_audio_and_video(audio_fp=audio_fp,vid_fp=vid_fp,output_fname='movie10s.webm',tmp_dir=ytd.tmp_dir)


    # workflow without downloading stuff 
def prep2(ytd,atts,vm):  # reads stuff dumped by prep - vids dir, subs_df, tts_df
    ytd.tmp_dir='tests'   
    atts.tmp_dir=atts.utils.path_join(ytd.tmp_dir,'audios')   # azure tmp dir
    f='They_Discovered_Advance_Tiny_Humans_Living_In_A_Fridge.pl.json3' # or use the old ones 
    ytd.subs_fp=ytd.utils.path_join(ytd.tmp_dir,f)
    ytd.parse_json3_to_df()                                 # parse subs to df 
    ytd.concat_on_time(N=30)                                # concat on 30s chunks 
    f='tts_df.csv' # or use the old ones 
    fp=ytd.utils.path_join(ytd.tmp_dir,f)
    #atts.tts_df = atts.utils.read_df(fp)
    chunks=['chunk_0_0-08_299-92.wav','chunk_1_297-76_588-03.wav']
    chunks_fps=[ytd.utils.path_join(atts.tmp_dir,i) for i in chunks ] 
    vm.concat_audios(audios_fps=chunks_fps
                     ,output_dir_fp=atts.tmp_dir
                     ,output_fname='chunks_combined.wav')
    
    f='THEY_DISCOVERED_ADVANCE_TINY_HUMANS_LIVING_IN_A_FRIDGE.webm'
    ytd.vid_fp=ytd.utils.path_join(ytd.tmp_dir,f)
    
    
    ytd_vid_len=vm.get_media_len(ytd.vid_fp)                                         # 586.211
    chunks_len=sum([ vm.get_media_len(chunk_fp) for chunk_fp in chunks_fps ])        # 558.233
    wavs_len=sum([ vm.get_media_len(fp) for fp in atts.tts_df['wav_fp'].to_list() ]) # 575.6579   
    slippage=(ytd_vid_len - wavs_len ) / len(atts.tts_df)


    print(f'ytd vid len {ytd_vid_len}')
    print(f'chunks_len {chunks_len}')
    print(f'wavs_len {wavs_len}')
    
    if slippage < 0: # video longer than audio - add pauses to video 
        print('audio longer than video - add pauses to video ')

    
    if slippage >=0:
        print('audio shorter than video - add pauses to audio  ')
            
    vids2_dir=ytd.utils.path_join(ytd.tmp_dir,'vids2')
    
    
    
     




now=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
urls=['https://www.youtube.com/watch?v=qY3djlib86s&ab_channel=LiftingVault'
      ,'https://www.youtube.com/watch?v=qY3djlib86s&ab_channel=LiftingVault'
      ,'https://www.youtube.com/watch?v=qY3djlib86s&ab_channel=LiftingVault'
]


urls=[
    'https://www.youtube.com/watch?v=RSJFxUiGNzw&ab_channel=MovieRecaps'
    ,'https://www.youtube.com/watch?v=2IA3AXpAdEg&ab_channel=MovieRecaps'
    ,'https://www.youtube.com/watch?v=75nuQP7UYnE&ab_channel=MovieRecaps'
]
movs=['Prehistoric_Creatures_Immune_to_Modern_Weapons_Suddenly_Appear_in_Los_Angeleswebm.webm'
      ,'Farmer_Accidentally_Shoots_Into_an_Oil_Well_and_Gets_1_Billion_Offerwebm.webm'
      ,'Scientists_Impregnate_a_Woman_With_Gods_DNA_But_The_Result_Isnt_a_Babywebm.webm'
      ]
dirs=['2023040811__0','2023040811__1','2023040811__2']


for no,urll in enumerate(urls):
    yt=ytd(utils(), url())
    at=atts(utils())
    at.lang='pl'
    at.config='azure.json'
    #atts.talk()
    #exit(1)
    v=vm(utils())
    now=datetime.datetime.now().strftime("%Y%m%d%H") + f'__{str(no)}'
    vid=movs[no]
    prep_offline(ytd=yt,atts=at,vm=v,url=urll,tmp_dirname=dirs[no],mov=vid)


#prep2(ytd,atts)
#print(atts.tts_df)
#
