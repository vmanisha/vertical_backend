import matplotlib.pyplot as plt
import numpy as np

Verticals = ['image','video','wiki','organic']
vert_color = ['blue','black','cyan','green']

def SetVisBox(bp):
	plt.setp(bp['boxes'][0], color=vert_color[0])
	plt.setp(bp['boxes'][1], color=vert_color[1])
	plt.setp(bp['boxes'][2], color=vert_color[2])
	plt.setp(bp['boxes'][3], color=vert_color[3])

  


def PlotVisiblityStats(visibility,visible_time):
	fig = plt.figure()
	ax = plt.axes()
	plt.hold(True)

	for cid in range(0,5):
		time_data = [visible_time['i'][cid], visible_time['v'][cid], visible_time['w'][cid], visible_time['o'][cid]]
		sp = (cid*4)+cid+1
		pos = [sp, sp+1, sp+2, sp+3]
		bp = plt.boxplot(time_data,positions=pos,widths=0.5,sym='')
		# means = [np.mean(data) for data in time_data]
		# ax.plot(pos,means,'rs')
		SetVisBox(bp)

	# set axes limits and labels
	plt.xlim(0,25)
	plt.ylim(0,120)
	plt.xlabel('Document Positions')
	plt.ylabel('Viewport Time (seconds)')
	plt.title('Document Viewport Times (sec) ')
	ax.set_xticklabels(['1', '2', '3', '4', '5'])
	ax.set_xticks([2.5, 7.5, 12.5, 17.5, 22.5])

	# draw temporary red and blue lines and use them to create a legend
	h1, = plt.plot([1,1],color=vert_color[0])
	h2, = plt.plot([1,1],color=vert_color[1])
	h3, = plt.plot([1,1],color=vert_color[2])
	h4, = plt.plot([1,1],color=vert_color[3])
	plt.legend((h1,h2,h3,h4),Verticals)
	h1.set_visible(False)
	h2.set_visible(False)
	h3.set_visible(False)
	h4.set_visible(False)

	plt.savefig('card_time_per_vert.png')
	plt.show()

def PlotTaskSat(satisfaction):
	plt.figure()

	sat_data = []
	sat_data.append(satisfaction['i'])
	sat_data.append(satisfaction['v'])
	sat_data.append(satisfaction['w'])
	sat_data.append(satisfaction['o'])

	plt.boxplot(sat_data)
	plt.ylim(0,4)
	plt.ylabel('Satisfaction Ratings')
	plt.xlabel('Verticals')

	plt.savefig('task_sat_per_vert.png')
	plt.show()
