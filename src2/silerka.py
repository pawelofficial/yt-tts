import ytd 
import datetime
import azure_tts
import vid_maker as vm 

def ytd_wf1(ytd: ytd
        ,url='https://www.youtube.com/watch?v=_ypD5iacrnI&ab_channel=MovieRecaps'
        ,download_timestamps=True
        ,download_vid=True
        ,lang='pl'
        ,clear_tmp = True ):

    dir_name=datetime.datetime.now().strftime("%Y%m%d%H%M")     # make a dir with minutes 
#    dir_name=datetime.datetime.now().strftime("%Y%m%d%H")     # make a dir  till hours 
    dir_fp=ytd.path_join(ytd.tmp_dir, dir_name)             # make a dir 
    ytd.make_dir(fp=dir_fp)
    ytd.tmp_dir= dir_fp                                     # set a dir 
    if clear_tmp:
        ytd.clear_dir(fp=ytd.tmp_dir)
    if download_vid:
        if download_timestamps:
            timestamps=None # ["00:00:00","00:1:00"]
            ytd.download_vid(yt_url=url,timestamps=timestamps)
        else:
            ytd.download_vid(yt_url=url)
            
    # download whole thing 
    ytd.download_subs(yt_url=url,lang=lang)                 # download subs 
    df_fp=ytd.parse_json3_to_df(fp=ytd.subs_fp,dump_all=True,N=60)     # parse subs, dump all
    return df_fp,ytd.tmp_dir,ytd.vid_fp

def tts_wf1(ytd):
    a=azure_tts.azure_tts()
    #a.talk()
    a.set_lang='pl'                                             # set language 
    a.tmp_dir=ytd.tmp_dir                                       # rewrite tmp dir 
    a.vids_dir=a.make_dir(fp=a.path_join(a.tmp_dir,'vids'))     # make vids dir 
    a.clear_dir(fp=a.vids_dir)                              # clear if you're running it again
    df_fp=a.path_join(a.tmp_dir,'df_parsed.csv')            # get df fp 
    a.read_df(df_fp=df_fp)                                  # read it 
    df=ytd.subs_df
    txt=' '.join(df['txt'].to_list()).strip()
    print(txt)
    txt=ytd.fuzzy_cutoff(s=txt,fuzzy_string='dzieki za ogladanie',append_txt='Dzieki za ogladanie kanalu siłerka, koniecznie go zasubskrybuj i do zobaczenia!')
    print(txt)
    txt=ytd.fuzzy_startoff(s=txt,fuzzy_string='liftvault',prepend_txt='Siemanko, witaj na kanale siłerka!')
    
    print(txt)
    input('wait1')
    audio_fp,len=a.make_a_vid(txt=txt,rate=1)   
    return audio_fp,len

def vidmaker_wf(vid_fp,speech_fp,background_fp,working_dir_fp,do_all=True):
    i=vm.vid_maker()
    # 1. split raw yt video audio and video  
    print('splitting raw vid ')
    if 0 or do_all:
        yt_vid_fp,yt_vid_audio_fp=i.split_sound_and_video(vid_fp=vid_fp
                                                                ,out_dir=working_dir_fp
                                                                ,do_audio=True
                                                                ,do_video=True)
    else:
        yt_vid_fp=i.path_join(working_dir_fp,'_vid_only.webm')
        yt_vid_audio_fp=i.path_join(working_dir_fp,'_audio_only.mp3')
        
    # 2 cur vid to some timestamps 
    print('cutting video ')
    if 0 or do_all:
        dur_flt=15
        cut_vid_fp=i.path_join(working_dir_fp,'cut_vid.webm')
        cut_vid_fp=i.torch_cut_vid(vid_fp=yt_vid_fp,out_fp=cut_vid_fp,st_flt=5,en_flt=-15)
        dur_flt=i.get_vid_len(cut_vid_fp)
    else:
        cut_vid_fp=i.path_join(working_dir_fp,'cut_vid.webm')
        
    print(' concating video ')
    # 3. concat vid so they're longer than speech fp 
    if 0 or do_all:
        speech_fp_len=i.get_vid_len(speech_fp)
        N=int(speech_fp_len // (dur_flt) + 1) 
        concat_cut_vid_fp=i.path_join(working_dir_fp,'concat_cut_vid.webm')
        concat_cut_vid_fp=i.concat_streams(fps=[cut_vid_fp for i in range(N)],out_fp=concat_cut_vid_fp)
    else:
        concat_cut_vid_fp=i.path_join(working_dir_fp,'concat_cut_vid.webm')
    
    #4. concat speech and background 
    print('concat speech and background')
    if 0 or do_all:
        speech_and_background_fp=i.path_join(working_dir_fp,'speech_and_background.wav')
        speech_and_background_fp=i.overlay_audios(speech_fp=speech_fp,background_fp=background_fp,out_fp=speech_and_background_fp)
    else:
        speech_and_background_fp=i.path_join(working_dir_fp,'speech_and_background.wav')
        
    # 5. cut vid so it's length is exactly the same as speech 
    print('cut video exactly to speech ')
    if 0 or do_all:
        exact_vid_fp=i.path_join(working_dir_fp,'exact_vid.webm')
        exact_vid_fp=i.torch_cut_vid(vid_fp=concat_cut_vid_fp,out_fp=exact_vid_fp,st_flt=0,dur_flt=i.get_vid_len(speech_fp))
    else:
        exact_vid_fp=i.path_join(working_dir_fp,'exact_vid.webm')
        
    #6. concat vid and audio 
    print('concat video and speech ')
    mov_fp=i.path_join(working_dir_fp,'mov.webm')
    mov_fp=i.overlay_audio_and_video(vid_fp=exact_vid_fp,audio_fp=speech_and_background_fp,out_fp=mov_fp)
        
        
if __name__=='__main__':
    ytd=ytd.ytd()
    background_fp=ytd.path_join('tmp','background_music_6m.wav')
    url='https://www.youtube.com/watch?v=_yd8dV_7oho&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=rz-hHjQPaQE&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=xhSSmrdQAUQ&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=x3UcrkMyEA0&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=N3xLz1BwUNo&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=u-GXZ5u3vaU&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=u-GXZ5u3vaU&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=DSfyvj7t6sA&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=BVbKjqg2HSw&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=gT8Z2QMr8eY&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=r5EKkQbx18c&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=BVbKjqg2HSw&ab_channel=LiftingVault'
#    url='https://www.youtube.com/watch?v=u-GXZ5u3vaU'
    
    # download vid and subs from lidting vault   + parse subs 
    df_fp,dir_name,vid_fp=ytd_wf1(ytd=ytd
        ,url=url
        ,download_timestamps=False
        ,download_vid=0
        ,clear_tmp=0
        ,lang='en'
        )
    exit(1)
    #  read subs via azure tts 
    speech_fp,audio_len=tts_wf1(ytd=ytd)
    
    # do some movie processing so it looks good 
    vidmaker_wf(vid_fp=vid_fp,
                speech_fp=speech_fp,
                background_fp=background_fp
                ,working_dir_fp=dir_name)
    
    
    
    

    



