

from Utils import Utils as utils
from ytURL import ytURL as url
from ytDownloader import ytDownloader as  ytd_ 
from azureTTS import azureTTS as atts_
from vidMaker import vidMaker as vm_ 
import time 
import datetime 


def download_vids():
    pass


if __name__=='__main__':
    urls=['https://www.youtube.com/watch?v=UsKN0nlkA34&ab_channel=belangp'
          ,'https://www.youtube.com/watch?v=mQExk0xl4_E&ab_channel=belangp'
          ,'https://www.youtube.com/watch?v=i7lb1nzQftc&ab_channel=belangp'
          ,'https://www.youtube.com/watch?v=sfjU3ugng7o&ab_channel=belangp'
          ,'https://www.youtube.com/watch?v=qP6vHHcYF9Y&ab_channel=belangp'
          ,'https://www.youtube.com/watch?v=lRVqJky9J6c&ab_channel=belangp'
          ,'https://www.youtube.com/watch?v=5ADtwpTbGF0&ab_channel=belangp'
          ,'https://www.youtube.com/watch?v=wx87Hv2WdwY&ab_channel=belangp'
          ,'https://www.youtube.com/watch?v=jZ3d415TAas&ab_channel=belangp'] 
          
    for url_ in urls:
        ytd=ytd_(utils(), url())
        ytd.tmp_dir=f'bElangp_pl_{ytd.utils.get_cur_ts()}' # ytd.utils.get_cur_ts()+'_belang'

        ytd.url=url_
        vid_fp=ytd.download_vid()
        ytd.download_subs(lang='en')
        ytd.parse_json3_to_df()
        ytd.concat_on_time(N=300)  
        ytd.punctuate_df(input_col='txt',output_col='txt')
        
        ytd.utils.dump_df(df=ytd.subs_df,fp=ytd.tmp_dir,name=ytd.vid_title)
        ###exit(1)
        ###fp=ytd.utils.path_join('tests','tests_inputs','belangp_subs_df_en_pl.csv')
        ###ytd.subs_df=ytd.utils.read_df(fp=fp)
        
    # make audio files 
        at=atts_(utils())
        at.lang='pl'
        at.config='azure.json'
        at.tmp_dir=at.utils.path_join(ytd.tmp_dir,'audios')
        at.translate(df=ytd.subs_df, text_column='txt',output_col='txt_pl',tgt_lang='pl')
        at.tts_from_df (df=ytd.subs_df,colname='txt_pl')
        at.utils.dump_df(df=at.tts_df,fp=ytd.tmp_dir,name='tts_df')

        # to delete 
        # tts_df=ytd.utils.read_df(fp=ytd.tmp_dir,name='tts_df.csv') 
        # vid_fp=ytd.utils.path_join(ytd.tmp_dir,'LBMA_Storage_and_the_Gold_to_Silver_Ratiowebm.webm')
        tts_df=at.tts_df
        vid_fp=ytd.vid_fp
    
        
    # make video 
        vm=vm_(utils())
        vm.tmp_dir=vm.utils.path_join(ytd.tmp_dir,'videos')
        combined_audio=vm.concat_audios(audios_fps=tts_df['wav_fp'].tolist(), output_fname='combined.wav')
        combined_audio_fp=vm.utils.path_join(vm.tmp_dir,'combined_mathed.wav')
        combined_audio_matched,_=vm.match_audio_len_to_video_exactly(audio_fp=combined_audio,vid_fp=vid_fp,audio_out_fp=combined_audio_fp)

        titles_ns=[]
        nsec=2
        audio_len=vm.get_media_len(combined_audio)
        vid_len=vm.get_media_len(vid_fp)
        N =int ( (audio_len-vid_len  ) / nsec ) # 15.5 
        titles_ns.append( f'{ytd.vid_title} :  {N} rozjazd' )
        movies_dir=vm.utils.path_join(vm.tmp_dir,'tmp','movies')
        vm.concat_audio_and_video(audio_fp=combined_audio_matched,vid_fp=vid_fp,output_fname=f'{ytd.vid_title}_movie.webm',tmp_dir=ytd.movies_dir)        

    for t in titles_ns:
        print(t)