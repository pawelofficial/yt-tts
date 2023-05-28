import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import ytDownloader
import Utils
import ytURL

def set_ytd():
    utils=Utils.Utils()
    yturl=ytURL.ytURL()
    ytdownloader=ytDownloader.ytDownloader(utils=utils,ytURL=yturl)
    return ytdownloader,utils,yturl


def unittest__set_url(url = None): # put into unittests
    if url is None:
        url='https://www.youtube.com/watch?v=GQ-k8i7qkMw&ab_channel=KinoCheck.com'
    ytd,utils,yturl=set_ytd()
    ytd.url=url
    #print(ytd.url)
    #print(ytd.ytURL.channel_url)
    #print(ytd.ytURL.channel)
    #print(ytd.ytURL.url_d)
    
def unittest__set_tmp_dir(dir = None): # put into unittests
    ytd,utils,yturl=set_ytd()
    ytd.tmp_dir=utils.get_cur_ts()
    print(ytd.tmp_dir)
    #print(ytd.tmp_dir)
    
def unittest__set_logger(): # put into unittests
    ytd,utils,yturl=set_ytd()
    ytd.logger='ytd_logger'
    
def unittest__download_vid():
    url='https://www.youtube.com/watch?v=wVvhBr64odI&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=BsNP5ygW-AM&ab_channel=UMCS'
    url='https://www.youtube.com/watch?v=hA02sLRC2KA&ab_channel=LiftingVault'
    ytd,utils,yturl=set_ytd()
    ytd.url=url                             # set url 
    ytd.tmp_dir=ytd.utils.get_cur_ts()      # set tmp dir
    ytd.download_vid()                      # download vid 
    
def unittest__download_vid_with_timestamps():   # doesnt work -,- 
    url='https://www.youtube.com/watch?v=wVvhBr64odI&ab_channel=LiftingVault'
    ytd,utils,yturl=set_ytd()
    ytd.url=url                             # set url 
    ytd.tmp_dir=ytd.utils.get_cur_ts()      # set tmp dir
    timestamps=['00:00:30','00:01:00']      # "00:00:00","00:1:00
    ytd.download_vid()                      # download vid 

def unittest__download_subs(lang='pl-pl'):   # doesnt work -,- 
    url='https://www.youtube.com/watch?v=AzqVHWEGcFY&ab_channel=MovieRecaps'
    url='https://www.youtube.com/watch?v=BsNP5ygW-AM&ab_channel=UMCS'
    ytd,utils,yturl=set_ytd()
    ytd.url=url                             # set url 
    ytd.tmp_dir=ytd.utils.get_cur_ts()      # set tmp dir
    ytd.download_subs(lang=lang)                      # download vid 
    ytd.parse_json3_to_df()
    ytd.utils.dump_df(df=ytd.subs_df,fp=ytd.tmp_dir,name='subs_df')
    
def unittest__check_available_subs_langs(lang='pl'):   # doesnt work -,- 
    url='https://www.youtube.com/watch?v=AzqVHWEGcFY&ab_channel=MovieRecaps'
    url='https://www.youtube.com/watch?v=BsNP5ygW-AM&ab_channel=UMCS'
    ytd,utils,yturl=set_ytd()
    ytd.url=url                             # set url 
    ytd.tmp_dir=ytd.utils.get_cur_ts()      # set tmp dir
    isavailable,langs_d=ytd.check_available_subs_langs(lang=lang)                      # download vid 
    print(isavailable)
    print(langs_d.keys())

    
def unittest__parse_json3_to_df():
    ytd,utils,yturl=set_ytd()
    j='They_Discovered_Advance_Tiny_Humans_Living_In_A_Fridge.pl.json3'
    json3_fp=utils.path_join('tests','tests_inputs',j)
    ytd.subs_fp=json3_fp
    ytd.parse_json3_to_df()
    print(ytd.subs_df)

def unittest_get_chunk_of_subs():
    ytd,utils,yturl=set_ytd()
    j='They_Discovered_Advance_Tiny_Humans_Living_In_A_Fridge.pl.json3'
    json3_fp=utils.path_join('tests','tests_inputs',j)
    ytd.subs_fp=json3_fp
    ytd.parse_json3_to_df()
    d=ytd.get_chunks_of_subs()
    

    
def unittest__concat_overlapping_rows():
    ytd,utils,yturl=set_ytd()
    fp=utils.path_join('tests','tests_inputs','tasmania_df.csv')
    ytd.subs_df=ytd.utils.read_df(fp=fp)    
    df=ytd.concat_overlapping_rows()
    fp=utils.path_join('tests','tests_outputs')
    ytd.utils.dump_df(df=ytd.subs_df,fp=fp,name='tasmania_df_parsed')
    
    ###    fp=utils.path_join('tests','tests_inputs','tasmania_df.csv')
    ###    ytd.subs_df=ytd.utils.read_df(fp=fp)    
    ###    df=ytd.concat_overlapping_rows(N=10)
    ###    fp=utils.path_join('tests','tests_outputs')
    ###    ytd.utils.dump_df(df=ytd.subs_df,fp=fp,name='tasmania_df_parsed_10s')
    ###

def unittest__download_and_aggregate(lang='en'):
    url='https://www.youtube.com/watch?v=AzqVHWEGcFY&ab_channel=MovieRecaps'
    url='https://www.youtube.com/watch?v=jZ3d415TAas&ab_channel=belangp'
    ytd,utils,yturl=set_ytd()

    
    ytd.url=url                             # set url 
    ytd.tmp_dir=ytd.utils.get_cur_ts()      # set tmp dir
    ytd.download_subs(lang=lang)                      # download vid 
    ytd.parse_json3_to_df()
    ytd.utils.dump_df(df=ytd.subs_df,fp=ytd.tmp_dir,name=ytd.vid_title)
    ytd.concat_on_time()
    ytd.utils.dump_df(df=ytd.subs_df,fp=ytd.tmp_dir,name=f'time_{ytd.vid_title}')
    print(ytd.subs_df)

    


if __name__=='__main__':
    unittest__download_vid()
    exit(1)
    unittest__check_available_subs_langs()
    unittest__download_subs()
#    unittest__download_vid()
#    unittest__set_tmp_dir()
#    unittest__download_and_aggregate()
#    unittest_get_chunk_of_subs()
    if 0:
        unittest__set_url()
        unittest__set_tmp_dir()
        unittest__set_logger()
    #unittest__download_vid()
#    unittest__download_subs()
#    unittest__parse_json3_to_df()
#    unittest__concat_overlapping_rows()
 