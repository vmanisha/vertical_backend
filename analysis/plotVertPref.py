import matplotlib.pyplot as plt
import numpy as np

# new_df_sum = new_df.sum(axis=1)
# print new_df, new_df_sum

# data = new_df.values

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

plt.rc('font', **font)

topics = ['BMW C1 motorcycle','Bachelor party ideas','Dewar Flask','Dumb blonde jokes', \
	'Inertia of sphere','Kim Kardashian','Kobe bryant','Long beach california', \
	'Varese ionisation','Xmen sequel']
verticals = ['General Web','Images','Videos','Wiki','Others']

desktop_data = [[0.54545454545454541, 0.0, 0.0, 0.45454545454545453], \
	[0.36363636363636365, 0.27272727272727271, 0.0, 0.36363636363636365], \
	[0.0, 0.36363636363636365, 0.45454545454545453, 0.18181818181818182],\
	[0.36363636363636365, 0.18181818181818182, 0.45454545454545453, 0.0],\
	[0.090909090909090912, 0.27272727272727271, 0.36363636363636365, 0.27272727272727271],\
	[0.27272727272727271, 0.18181818181818182, 0.36363636363636365, 0.18181818181818182],\
	[0.0, 0.18181818181818182, 0.45454545454545453, 0.36363636363636365],\
	[0.090909090909090912, 0.18181818181818182, 0.63636363636363635, 0.090909090909090912],\
	[0.0, 0.0, 0.72727272727272729, 0.27272727272727271],\
	[0.27272727272727271, 0.0, 0.18181818181818182, 0.54545454545454541]]

mobile_data = [[0.83333333333333337, 0.0, 0.16666666666666666, 0.0], \
	[0.16666666666666666, 0.5, 0.33333333333333331, 0.0], \
	[0.0, 0.80000000000000004, 0.20000000000000001, 0.0], \
	[1.0, 0.0, 0.0, 0.0], \
	[0.16666666666666666, 0.0, 0.16666666666666666, 0.66666666666666663], \
	[0.16666666666666666, 0.0, 0.66666666666666663, 0.16666666666666666], \
	[0.0, 0.33333333333333331, 0.5, 0.16666666666666666], \
	[0.0, 0.0, 0.5, 0.5], \
	[0.0, 0.14285714285714285, 0.14285714285714285, 0.7142857142857143], \
	[0.375, 0.0, 0.125, 0.5]]

app_data = [[0.2857142857,	0.6666666667,	0.2857142857,	0.380952381,	0.04761904762],\
	[0.5769230769,	0.3461538462,	0.1538461538,	0.2307692308,	0.07692307692], \
	[0.1176470588,	0.5294117647,	0.1764705882,	0.5882352941,	0.05882352941], \
	[0.6666666667,	0.4285714286,	0.1428571429,	0.1904761905,	0.1428571429], \
	[0.5,	0.375,	0.2083333333,	0.7083333333,	0.08333333333], \
	[0.5217391304,	0.7391304348,	0.1739130435,	0.3043478261,	0.04347826087], \
	[0.3125,	0.375,	0.125,	0.6875,	0.125], \
	[0.4166666667,	0.6666666667,	0.04166666667,	0.5,	0.1666666667], \
	[0.4,	0.2,	0.6666666667,	0.6,	0.06666666667], \
	[0.7,	0.4,	0.4,	0.3,	0]]

fig, ax = plt.subplots()
# data = np.array(desktop_data)
# data = np.array(mobile_data)
data = np.array(app_data)
for y in range(data.shape[0]):
    for x in range(data.shape[1]):
        col = 'black'
        if y == 0 and x == 0:
            col = 'white'
        #print data[y, x], new_df_sum[y], x, y
        plt.text(x + 0.5 , y + 0.5, '%2.2f' % (data[y,x]), \
            horizontalalignment='center',\
            verticalalignment='center',\
            color=col,size=15)

heatmap = ax.pcolor(data, cmap=plt.cm.Blues)

# put the major ticks at the middle of each cell
ax.set_xticks(np.arange(data.shape[1])+0.5)#, minor=False)
ax.set_yticks(np.arange(data.shape[0])+0.5)#, minor=False)
# ax.set_ylabel('Topics',fontsize=15)
# ax.set_xlabel('Verticals',fontsize=15)
# want a more natural, table-like display
ax.invert_yaxis()
ax.xaxis.tick_top()

ax.set_xticklabels(verticals, minor=False,fontsize=15)
ax.set_yticklabels(topics, minor=False,fontsize=15)
plt.show()