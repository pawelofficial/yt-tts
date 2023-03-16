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
    assert a1 == True  and a2 == True and a3==True and a4==True and a5==True 
    

    
    
        
if __name__=='__main__':
    test_invoke_ytd()

