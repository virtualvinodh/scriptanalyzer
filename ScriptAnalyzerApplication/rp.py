import rpy2.robjects as R

import scipy.stats as stats

a = [1,2,3,4]*2
b = [21,32,43,51]*2
c = [56,12,12,23]*2

result = R.r['t.test'](R.IntVector(a),R.IntVector(b))

k =  str(result)[str(result).find('p-value = '):]

print k