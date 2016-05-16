'''
Created on 1 Jun 2015

@author: Administrator
'''

import matlab.engine
eng = matlab.engine.start_matlab()
eng.tr.tri(nargout=0)