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
def test_path_join_swap():
    """ tests whether invoking wizard works and variables are initiated  """
    i=ut.utils()
    fp=i.path_join('tests','tests_inputs','path_join_swap.txt') # file that exists in a path 
    fp2=i.path_join(fp,'dummy_file2.txt',swap=True)             # you wish to simply swap the file
    
    a1 =  os.path.dirname(fp)==os.path.dirname(fp2) 
    a2 = os.path.split(fp)[1] != os.path.split(fp2)[1]
    assert a1 & a2 
    
        
if __name__=='__main__':
    test_path_join_swap()

