import matplotlib.pyplot as plt
import numpy as np

vert = ['i','v','w','o']
verticals = ['Image','Video','Wiki','Organic']
vert_color = ['blue','black','cyan','green']

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

plt.rc('font', **font)

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
        # sym='' for not showing outliers
        bp = plt.boxplot(time_data,positions=pos,widths=0.5,sym='')
        # means = [np.mean(data) for data in time_data]
        # ax.plot(pos,means,'rs')
        SetVisBox(bp)

    # set axes limits and labels
    plt.xlim(0,25)
    plt.ylim(0,120)
    plt.xlabel('Document Positions')
    plt.ylabel('Viewport Time (seconds)')
    # plt.title('Document Viewport Times (sec) ')
    ax.set_xticklabels(['1', '2', '3', '4', '5'])
    ax.set_xticks([2.5, 7.5, 12.5, 17.5, 22.5])

    # draw temporary red and blue lines and use them to create a legend
    h1, = plt.plot([1,1],color=vert_color[0])
    h2, = plt.plot([1,1],color=vert_color[1])
    h3, = plt.plot([1,1],color=vert_color[2])
    h4, = plt.plot([1,1],color=vert_color[3])
    plt.legend((h1,h2,h3,h4),verticals, loc='upper center',\
        bbox_to_anchor=(0.5, 1.05),ncol=4,fontsize=15)
    h1.set_visible(False)
    h2.set_visible(False)
    h3.set_visible(False)
    h4.set_visible(False)

    plt.savefig('view_port_time.png')
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
    plt.xticks([1,2,3,4],verticals, loc='upper center',\
        bbox_to_anchor=(0.5, 1.05),ncol=4,fontsize=15)

    plt.savefig('task_sat_per_vert.png')
    plt.show()


def PlotPageResponsePerVert(first_rel_group,last_rel_group):
    fig = plt.figure()
    ax = plt.axes()
    plt.hold(True)

    # On Relevance
    resp_data = []
    sp = 1
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
       resp_data.append(first_rel_group.get_group((v,'relevance'))['response_value'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    SetVisBox(bp)
    
    # On Satisfaction
    resp_data = []
    sp = pos[3]+2
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
       resp_data.append(first_rel_group.get_group((v,'satisfaction'))['response_value'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    SetVisBox(bp)
    
    plt.xlim(0,pos[3]+1)
    plt.ylim(0.5,5.5)
    plt.ylabel('Page Response')

    ax.set_xticklabels(['Relevance','Satisfaction'])
    ax.set_xticks([2.5, 7.5])

    # draw temporary red and blue lines and use them to create a legend
    h1, = plt.plot([1,1],color=vert_color[0])
    h2, = plt.plot([1,1],color=vert_color[1])
    h3, = plt.plot([1,1],color=vert_color[2])
    h4, = plt.plot([1,1],color=vert_color[3])
    plt.legend((h1,h2,h3,h4),verticals, loc='upper center',\
        bbox_to_anchor=(0.5, 1.05),ncol=4,fontsize=15)
    h1.set_visible(False)
    h2.set_visible(False)
    h3.set_visible(False)
    h4.set_visible(False)

    plt.savefig('rel_sat_first_pos.png')
    plt.show()

def PlotFirstAndLastClickRank(vertical_stats):
    fig = plt.figure()
    ax = plt.axes()
    plt.hold(True)

    # First Click Rank
    resp_data = []
    sp = 1
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
        print v,'first ranks', np.median(vertical_stats[v]['first_rank'])
        resp_data.append(vertical_stats[v]['first_rank'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    SetVisBox(bp)

    # Last Click Rank
    resp_data = []
    sp = pos[3]+2
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
        print v,'last ranks', np.median(vertical_stats[v]['last_rank'])
        resp_data.append(vertical_stats[v]['last_rank'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    SetVisBox(bp)
    
    # set axes limits and labels
    plt.xlim(0,pos[3]+1)
    plt.ylim(0.5,10.5)
    plt.ylabel('Result Rank')

    ax.set_xticklabels(['First Click','Last Click'])
    ax.set_xticks([2.5, 7.5])

    # draw temporary red and blue lines and use them to create a legend
    h1, = plt.plot([1,1],color=vert_color[0])
    h2, = plt.plot([1,1],color=vert_color[1])
    h3, = plt.plot([1,1],color=vert_color[2])
    h4, = plt.plot([1,1],color=vert_color[3])
    plt.legend((h1,h2,h3,h4),verticals, loc='upper center',\
        bbox_to_anchor=(0.5, 1.05),ncol=4, fontsize = 12)
    h1.set_visible(False)
    h2.set_visible(False)
    h3.set_visible(False)
    h4.set_visible(False)

    plt.savefig('first_last_rank.png')
    plt.show()


def PlotFirstAndLastClickTime(vertical_stats):
    fig = plt.figure()
    ax = plt.axes()
    plt.hold(True)

    # First Click Rank
    resp_data = []
    sp = 1
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
        print v,'first click', np.median(vertical_stats[v]['first_click'])
        resp_data.append(vertical_stats[v]['first_click'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    SetVisBox(bp)

    # Last Click Rank
    resp_data = []
    sp = pos[3]+2
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
        print v,'last click', np.median(vertical_stats[v]['last_click'])
        resp_data.append(vertical_stats[v]['last_click'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    SetVisBox(bp)
    
    # set axes limits and labels
    plt.xlim(0,pos[3]+1)
    plt.ylim(0,170)
    plt.ylabel('Time to Click (seconds)')

    ax.set_xticklabels(['First Click','Last Click'])
    ax.set_xticks([2.5, 7.5])

    # draw temporary red and blue lines and use them to create a legend
    h1, = plt.plot([1,1],color=vert_color[0])
    h2, = plt.plot([1,1],color=vert_color[1])
    h3, = plt.plot([1,1],color=vert_color[2])
    h4, = plt.plot([1,1],color=vert_color[3])
    plt.legend((h1,h2,h3,h4),verticals, loc='upper center',\
        bbox_to_anchor=(0.5, 1.05),ncol=4, fontsize = 12)
    h1.set_visible(False)
    h2.set_visible(False)
    h3.set_visible(False)
    h4.set_visible(False)

    plt.savefig('first_last_time.png')
    plt.show()


# def PlotPageResponsePerVert(first_rel_group,last_rel_group):
#     fig = plt.figure()
#     ax = plt.axes()
#     plt.hold(True)

#     # On Relevance
#     resp_data = []
#     sp = 1
#     pos = [sp, sp+1, sp+2, sp+3]
#     #for v in vert:
#     #    resp_data.append(first_rel_group.get_group((v,'relevance'))['response_value'])
#     for v in vert:
#         print v,'last ranks', np.median(first_rel_group[v]['last_rank'])
#         resp_data.append(first_rel_group[v]['last_rank'])
#     # sym='' for not showing outliers
#     bp = plt.boxplot(resp_data,positions=pos,widths=0.5)#,sym='')
#     SetVisBox(bp)
#     '''
#     # Off Relevance
#     resp_data = []
#     sp = pos[3]+2
#     pos = [sp, sp+1, sp+2, sp+3]
#     for v in vert:
#         resp_data.append(last_rel_group.get_group((v,'relevance'))['response_value'])
#     # sym='' for not showing outliers
#     bp = plt.boxplot(resp_data,positions=pos,widths=0.5,sym='')
#     SetVisBox(bp)
    
#     # On Satisfaction
#     resp_data = []
#     sp = pos[3]+2
#     pos = [sp, sp+1, sp+2, sp+3]
#     for v in vert:
#         resp_data.append(first_rel_group[v]['last_rank'])
#     #for v in vert:
#     #    resp_data.append(first_rel_group.get_group((v,'satisfaction'))['response_value'])
#     # sym='' for not showing outliers
#     bp = plt.boxplot(resp_data,positions=pos,widths=0.5)#,sym='')
#     SetVisBox(bp)
    
#     # Off Satisfaction
#     resp_data = []
#     sp = pos[3]+2
#     pos = [sp, sp+1, sp+2, sp+3]
#     for v in vert:
#         resp_data.append(last_rel_group.get_group((v,'satisfaction'))['response_value'])
#     # sym='' for not showing outliers
#     bp = plt.boxplot(resp_data,positions=pos,widths=0.5,sym='')
#     SetVisBox(bp)
#     '''
#     # set axes limits and labels
#     plt.xlim(0,pos[3]+1)
#     plt.ylim(0,12)
#     #plt.ylim(0,40)
#     # plt.xlabel('Page Response Type')
#     # plt.ylabel('Page Response')
#     # plt.ylabel('Result Rank')
#     # plt.ylabel('#clicks')
#     plt.ylabel('Result Rank')

#     # plt.title('Document Viewport Times (sec) ')
#     # ax.set_xticklabels(['Relevance','Satisfaction'])
#     ax.set_xticklabels(['Last Click Rank'])
#     #ax.set_xticklabels(['Number of clicks per SERP'])

#     ax.set_xticks([2.5]) #, 7.5]) #, 12.5, 17.5])

#     # draw temporary red and blue lines and use them to create a legend
#     h1, = plt.plot([1,1],color=vert_color[0])
#     h2, = plt.plot([1,1],color=vert_color[1])
#     h3, = plt.plot([1,1],color=vert_color[2])
#     h4, = plt.plot([1,1],color=vert_color[3])
#     plt.legend((h1,h2,h3,h4),verticals, loc='upper center',\
#         bbox_to_anchor=(0.5, 1.05),ncol=2, fontsize = 12)
#     h1.set_visible(False)
#     h2.set_visible(False)
#     h3.set_visible(False)
#     h4.set_visible(False)

#     #plt.savefig('page_resp_per_vert.png')
#     plt.savefig('first_last_rank.png')
#     plt.show()

def PlotDwellTimePerVert(vertical_stats):
	fig = plt.figure()
	ax = plt.axes()
	plt.hold(True)

	for cid in range(0,5):
		time_data = [vertical_stats['i']['pos_dwell'][cid], \
			vertical_stats['v']['pos_dwell'][cid], \
			vertical_stats['w']['pos_dwell'][cid], \
			vertical_stats['o']['pos_dwell'][cid]]
		sp = (cid*4)+cid+1
		pos = [sp, sp+1, sp+2, sp+3]
		bp = plt.boxplot(time_data,positions=pos,widths=0.5)
		SetVisBox(bp)

	plt.xlim(0,25)
	plt.ylim(0,180)
	plt.xlabel('Document Positions')
	plt.ylabel('Dwell Time (seconds)')
	ax.set_xticklabels(['1', '2', '3', '4', '5'])
	ax.set_xticks([2.5, 7.5, 12.5, 17.5, 22.5])

    # draw temporary red and blue lines and use them to create a legend
	h1, = plt.plot([1,1],color=vert_color[0])
	h2, = plt.plot([1,1],color=vert_color[1])
	h3, = plt.plot([1,1],color=vert_color[2])
	h4, = plt.plot([1,1],color=vert_color[3])
	plt.legend((h1,h2,h3,h4),verticals, loc='upper center',\
        bbox_to_anchor=(0.5, 1.05),ncol=4,fontsize=15)
	h1.set_visible(False)
	h2.set_visible(False)
	h3.set_visible(False)
	h4.set_visible(False)

	plt.savefig('dwell_time_per_vert.png')
	plt.show()


def PlotClickDistPerVertical(vertical_stats):
	fig = plt.figure()
	ax = plt.axes()
	plt.hold(True)

	ind = [1,6,11,16,21]
	time_data = vertical_stats['i']['clicks'].values()
	rect_i = ax.bar(ind,time_data,0.5,color=vert_color[0])

	ind = [x+1 for x in ind]
	time_data = vertical_stats['v']['clicks'].values()
	rect_v = ax.bar(ind,time_data,0.5,color=vert_color[1])

	ind = [x+1 for x in ind]
	time_data = vertical_stats['w']['clicks'].values()
	rect_w = ax.bar(ind,time_data,0.5,color=vert_color[2])

	ind = [x+1 for x in ind]
	time_data = vertical_stats['o']['clicks'].values()
	rect_o = ax.bar(ind,time_data,0.5,color=vert_color[3])

	ax.legend((rect_i,rect_v,rect_w,rect_o),verticals,loc='upper center',\
		bbox_to_anchor=(0.5, 1.05),ncol=4,fontsize=15)

	plt.xlim(0,25)
	plt.ylim(0,0.5)
	plt.xlabel('Document Positions')
	plt.ylabel('% Clicks')
	ax.set_xticklabels(['1', '2', '3', '4', '5'])
	ax.set_xticks([2.5, 7.5, 12.5, 17.5, 22.5])

	plt.savefig('click_dist_per_vert.png')
	plt.show()

def PlotClickDist(vertical_stats):
    fig = plt.figure()
    ax = plt.axes()

    click_data = []
    sp = 1
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
        click_data.append(vertical_stats[v]['all_clicks'])
    bp = plt.boxplot(click_data,positions=pos,widths=0.5)
    # SetVisBox(bp)

    # plt.xlim(0,25)
    plt.ylim(0,20)
    plt.ylabel('Number of Clicks on SERP')
    ax.set_xticklabels(verticals)

    plt.savefig('serp_click_count.png')
    plt.show()


def PlotScrollDepthPerVert(highest_card):
    fig = plt.figure()
    ax = plt.axes()

    scroll_data = []
    sp = 1
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
        scroll_data.append(highest_card[v])
    bp = plt.boxplot(scroll_data,positions=pos,widths=0.5)
    # SetVisBox(bp)

    # plt.xlim(0,25)
    plt.ylim(0,1.1)
    plt.ylabel('Page Depth (%)')
    ax.set_xticklabels(verticals)

    plt.savefig('scroll_depth.png')
    plt.show()

def PlotSwipeFreqPerVert(swipe_freq):
    fig = plt.figure()
    ax = plt.axes()
    plt.hold(True)

    # PanUp
    resp_data = []
    sp = 1
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
        resp_data.append(swipe_freq[v]['panup'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    SetVisBox(bp)

    # PanDown
    resp_data = []
    sp = pos[3]+2
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
        resp_data.append(swipe_freq[v]['pandown'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    SetVisBox(bp)

    plt.xlim(0,pos[3]+1)
    plt.ylim(0,45)
    plt.ylabel('Swipe Counts')
    ax.set_xticklabels(['Down', 'Up'])
    ax.set_xticks([2.5, 7.5])

    # draw temporary red and blue lines and use them to create a legend
    h1, = plt.plot([1,1],color=vert_color[0])
    h2, = plt.plot([1,1],color=vert_color[1])
    h3, = plt.plot([1,1],color=vert_color[2])
    h4, = plt.plot([1,1],color=vert_color[3])
    plt.legend((h1,h2,h3,h4),verticals, loc='upper center',\
        bbox_to_anchor=(0.5, 1.05),ncol=4,fontsize=15)
    h1.set_visible(False)
    h2.set_visible(False)
    h3.set_visible(False)
    h4.set_visible(False)

    plt.savefig('swipe_freq.png')
    plt.show()

def PlotSwipeDistPerVert(swipe_dist):
    fig = plt.figure()
    ax = plt.axes()
    plt.hold(True)

    # PanUp
    resp_data = []
    sp = 1
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
        resp_data.append(swipe_dist[v]['panup'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    SetVisBox(bp)

    # PanDown
    resp_data = []
    sp = pos[3]+2
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
        resp_data.append(swipe_dist[v]['pandown'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    SetVisBox(bp)

    plt.xlim(0,pos[3]+1)
    plt.ylim(0,6500)
    plt.xlabel('Direction of Swipe')
    plt.ylabel('Swipe Distance (px)')
    ax.set_xticklabels(['Down', 'Up'])
    ax.set_xticks([2.5, 7.5])

    # draw temporary red and blue lines and use them to create a legend
    h1, = plt.plot([1,1],color=vert_color[0])
    h2, = plt.plot([1,1],color=vert_color[1])
    h3, = plt.plot([1,1],color=vert_color[2])
    h4, = plt.plot([1,1],color=vert_color[3])
    plt.legend((h1,h2,h3,h4),verticals, loc='upper center',\
        bbox_to_anchor=(0.5, 1.05),ncol=4,fontsize=15)
    h1.set_visible(False)
    h2.set_visible(False)
    h3.set_visible(False)
    h4.set_visible(False)

    plt.savefig('swipe_dist.png')
    plt.show()
'''
def PlotClickDistPerVertical(click_dist):
    plt.figure()

    click_data = []
    click_data.append(click_dist['i'])
    click_data.append(click_dist['v'])
    click_data.append(click_dist['w'])
    click_data.append(click_dist['o'])

    # sym='' for not showing outliers
    plt.boxplot(click_data,sym='')
    plt.ylim(0,11)
    plt.yticks(range(1,11))
    plt.ylabel('Document Positions')
    plt.xlabel('Verticals')
    plt.xticks([1,2,3,4],verticals)

    plt.savefig('click_dist_per_vert.png')
    plt.show()
'''
