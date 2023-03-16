import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import pytest 
import vid_maker as vm 

import ytd 
import utils as ut
# to run tests cd to this dir \src\tests
#  issue  $ pytest in terminal 
#  issue $ pytest::test_my_method to run specific test  
#  issue $ pytest -m <marker> to issu markers 


@pytest.mark.ytd
def test_invoke_ytd():
    """ tests whether invoking wizard works and variables are initiated  """
    i=ytd.ytd()
    a1=i.vid_fp is None 
    a2=i.subs_fp is None 
    a3=i.subprocess_out is None 
    a4 =all([v is None for v in i.subs_d.values()])
    a5=i.subs_df.empty 
    #assert a1 == True  and a2 == True and a3==True and a4==True and a5==True 
    
@pytest.mark.ytd
def test_download_vid():
    """ downloads a vid and checks if it's there  """
    i=ytd.ytd()
    url='https://www.youtube.com/watch?v=UADcrh2pfpA&ab_channel=CrushClips'
    fp=i.download_vid(yt_url=url)
    fpp,meta=i.path_join('tmp',fp,meta=True)
    
    #assert meta[0] == True and i.vid_fp is not None 
    
@pytest.mark.ytd
def test_download_subs():
    """ downloads subs and checks if it's there  """
    i=ytd.ytd()
    url='https://www.youtube.com/watch?v=nAk8MagnDsY&ab_channel=PowerfulJRE'
    fp=i.download_subs(yt_url=url)
    fpp,meta=i.path_join('tmp',fp,meta=True)
    #assert meta[0] == True and i.subs_fp is not None 
    
    
@pytest.mark.ytd
def test_read_json3_to_df(files : list  = None ):
    i=ytd.ytd()
    if files is None:
        files=['DAVID_ATTENBOROUGHS__TASMANIA__WEIRD_AND_WONDERFUL.en.json3','PEOPLE_BECOME_IMMORTAL_BUT_EACH_PERSON_CAN_LIVE_ONLY_26_YEARS_UNLESS_THEY_EARN_MORE_TIME.pl-en.json3']
    
    i.tmp_dir=i.path_join('tests','tests_output')
    test_input_dir=i.path_join('tests','tests_inputs')   
    for no,f in enumerate(files):
        fp=i.path_join(test_input_dir,f)
        df=i.read_json3_to_df(fp=fp)                                    # method 
        out_fp,_=i.strip_extension(s=f)
        name='_'.join(f.split('_')[:2])
        out_fp=i.path_join(i.tmp_dir,f'df_out_test_read_json3_to_df_{name}.csv')
        print(out_fp)
        i.dump_df(df=df,fp=out_fp)
        
@pytest.mark.ytd
def test_concat_overlapping_rows(files : list  = None,clear_output=True,csv = None  ):
    i=ytd.ytd()
    if files is None:
        files=['DAVID_ATTENBOROUGHS__TASMANIA__WEIRD_AND_WONDERFUL.en.json3','PEOPLE_BECOME_IMMORTAL_BUT_EACH_PERSON_CAN_LIVE_ONLY_26_YEARS_UNLESS_THEY_EARN_MORE_TIME.pl-en.json3']

    i.tmp_dir=i.path_join('tests','tests_output')
    if clear_output:
        i.clear_dir(fp=i.tmp_dir)
    test_input_dir=i.path_join('tests','tests_inputs')   
    for no,f in enumerate(files):
        fp=i.path_join(test_input_dir,f)

        if csv is None:
            df=i.read_json3_to_df(fp=fp)                                    
        else:
            fp=i.path_join(test_input_dir,csv)
            df=i.read_csv(fp=fp)

        df=i.concat_overlapping_rows(df=df,N=0)
        out_fp,_=i.strip_extension(s=f)
        name='_'.join(f.split('_')[:2])
        out_fp=i.path_join(i.tmp_dir,f'df_concat_overlapping_rows_{name}.csv')
        print(out_fp)
        i.dump_df(df=df,fp=out_fp)

# makes a boomerang 
def test_boomerang(f='boomerang2.webm'):
    i=ytd.ytd()
    vid_fp=i.path_join('tests','tests_inputs',f)
    f='boomerang_out.webm'
    out_fp=i.path_join('tests','tests_output',f)
    i.boomerangize(vid_fp=vid_fp,out_fp=out_fp)
    
#    import vid_maker as vm 
#    vm=vm.vid_maker()
#    timestamps=['00:00:24','00:00:5']
#    vm.cut_vid_to_timestamps(vid_fp=vid_fp,out_fp=out_fp,timestamps=timestamps)

        
def get_vid_len(f='boomerang2.webm'):
#    i=ytd.ytd()
    i=vm.vid_maker()
    vid_fp=i.path_join('tests','tests_inputs',f)
    
    l=i.get_vid_len(vid_fp=vid_fp)
    print(l)
        
def chopify(f='boomerang2.webm'):
#    i=ytd.ytd()
    i=vm.vid_maker()
    vid_fp=i.path_join('tests','tests_inputs',f)
    dir=i.path_join('tests','tests_output','chopify')
    l=i.chopify(vid_fp=vid_fp,out_dir=dir)
    
def trim_start_end(f='trim_start_end.webm'):
    i=vm.vid_maker()
    vid_fp=i.path_join('tests','tests_inputs',f)
    out_fp=i.path_join('tests','tests_output',f)
    l=i.trim_start_and_end(vid_fp=vid_fp,out_fp=out_fp,
                           start=5,end=15)
        
if __name__=='__main__':
    trim_start_end()
#    chopify()
#    test_boomerang()
    exit(1)
        
        
if __name__=='__main__':
    print('tests')
    i=ytd.ytd()
    files=['DAVID_ATTENBOROUGHS__TASMANIA__WEIRD_AND_WONDERFUL.en.json3','PEOPLE_BECOME_IMMORTAL_BUT_EACH_PERSON_CAN_LIVE_ONLY_26_YEARS_UNLESS_THEY_EARN_MORE_TIME.pl-en.json3']
    files=['SIR_THATS_NOT_HOW_YOU_PUT_THE_PLATES_ON.pl.json3']
    test_read_json3_to_df(files=files)

    csv='concat_on_cond2.csv'
    test_concat_overlapping_rows(files=files,clear_output=False,csv=csv)
