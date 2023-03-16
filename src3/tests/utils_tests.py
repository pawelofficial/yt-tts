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


def unittest__path_join():
    """ how to use path join function """
    ytd,utils,yturl=set_ytd()
    fp=utils.path_join('tests','tests_inputs','test__path_join.txt') # get filepath of an object
    f='200_Frozen_People_Found_in_The_Middle_of_a_Desert_and_The_Government_Decides_To_Keep_it_a_Secret.pl.json3'
    fp=utils.path_join('tmp','2023030720',f)
    print(fp)
    fp,tup=utils.path_join(fp,meta=True)    # get fp and meta info of an object 
    print(tup)    
    fp=utils.path_join(fp,'newfile.txt',swap=True) # get fp based on other fp swaping the file only
    print(fp)
    #assert tup == {'isfile': True, 'isdir': False, 'exists': True}
    

def unittest__subprocess_run():
    ytd,utils,yturl=set_ytd()
    l=['dir']
    logger=utils.setup_logger(name='test_logger',log_file='test_logger.log')
    code,stdout,stderr=utils.subprocess_run(l=l,logger=logger)
    
def unittest__get_cur_ts():
     ytdownloader,utils,yturl = set_ytd()
     print(utils.get_cur_ts())
    
    
def unittest__make_dir():
    ytdownloader,utils,yturl=set_ytd()
    fp=utils.path_join('tests','tests_inputs','test_dir')
    utils.make_dir(fp=fp)
    
def unittest__sentesize():
    ytdownloader,utils,yturl=set_ytd()
    fp=utils.path_join('tests','tests_inputs','tasmania_df.csv')
    df=utils.read_df(fp=fp)
    utils.sentesize(df=df)
    
    print(df)
    
    
    
    
    
    
    
    
    
    
if __name__=='__main__':
    unittest__path_join()
    exit(1)
    if 0:
        unittest__subprocess_run()
    unittest__get_cur_ts()
    unittest__make_dir()
 