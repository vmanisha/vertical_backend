import matplotlib.pyplot as plt
import numpy as np
import graphviz as gv

vert = ['i','v','w','o']
verticals = ['Image','Video','Wiki','Organic']
vert_color = ['blue','black','red','green']
vert_expand = {'i':'Image','v': 'Video', 'w': 'Wiki', 'o': 'Organic'}

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

plt.rc('font', **font)

def SetVisBox(bp):
    plt.setp(bp['boxes'][0], color=vert_color[0])
    plt.setp(bp['boxes'][1], color=vert_color[1])
    plt.setp(bp['boxes'][2], color=vert_color[2])
    plt.setp(bp['boxes'][3], color=vert_color[3])

def SetVisBoxForOnOff(bp):
    plt.setp(bp['boxes'][0], color=vert_color[0])
    plt.setp(bp['boxes'][1], color=vert_color[1])

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
    '''
    sat_data.append(satisfaction['i'])
    sat_data.append(satisfaction['v'])
    sat_data.append(satisfaction['w'])
    sat_data.append(satisfaction['o'])
    '''
    sat_data.append(satisfaction['on'])
    sat_data.append(satisfaction['off'])

    plt.boxplot(sat_data)
    plt.ylim(0,4)
    plt.ylabel('Satisfaction Ratings')
    plt.xlabel('Verticals')
    #plt.xticks([1,2,3,4],verticals, loc='upper center',\
    #    bbox_to_anchor=(0.5, 1.05),ncol=4,fontsize=15)

    plt.legend(['On','Off'],['On','Off'], loc='upper center',\
        bbox_to_anchor=(0.5, 1.05),ncol=2,fontsize=15)
    
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
    '''
    #pos = [sp, sp+1, sp+2, sp+3]
    pos = [sp, sp+1]
    for v in ['on','off']:
    #for v in vert:
        print v,'first ranks', np.median(vertical_stats[v]['first_rank'])
        resp_data.append(vertical_stats[v]['first_rank'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    # SetVisBox(bp)
    SetVisBoxForOnOff(bp)
    '''
    
    # Last Click Rank
    resp_data = []
    #sp = pos[1]+2
    #pos = [sp, sp+1, sp+2, sp+3]
    pos = [sp, sp+1]
    for v in ['on','off']:
    #for v in vert:
        print v,'last ranks', np.median(vertical_stats[v]['last_rank'])
        resp_data.append(vertical_stats[v]['last_rank'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    #SetVisBox(bp)
    SetVisBoxForOnOff(bp)
    
    # set axes limits and labels
    plt.xlim(0,pos[1]+1)
    plt.ylim(0.5,11)
    plt.ylabel('Result Rank')

    ax.set_xticklabels(['Last Click'])#,'Last Click'])
    #ax.set_xticks([2.5, 7.5])
    ax.set_xticks([1.5])#, 4.5])

    # draw temporary red and blue lines and use them to create a legend
    h1, = plt.plot([1,1],color=vert_color[0])
    h2, = plt.plot([1,1],color=vert_color[1])
    #h3, = plt.plot([1,1],color=vert_color[2])
    #h4, = plt.plot([1,1],color=vert_color[3])
    #plt.legend((h1,h2,h3,h4),verticals, loc='upper center',\
    #    bbox_to_anchor=(0.5, 1.05),ncol=4, fontsize = 12)
    plt.legend((h1,h2),['On','Off'], loc='upper center',\
        bbox_to_anchor=(0.5, 1.05),ncol=2, fontsize = 12)
    h1.set_visible(False)
    h2.set_visible(False)
    #h3.set_visible(False)
    #h4.set_visible(False)

    plt.savefig('first_last_rank.png')
    plt.show()


def PlotFirstAndLastClickTime(vertical_stats):
    fig = plt.figure()
    ax = plt.axes()
    plt.hold(True)
    '''
    # First Click Rank
    resp_data = []
    sp = 1
    #pos = [sp, sp+1, sp+2, sp+3]
    pos = [sp, sp+1]
    #for v in vert:
    for v in ['on','off']:
        print v,'first click', np.median(vertical_stats[v]['first_click'])
        resp_data.append(vertical_stats[v]['first_click'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    #SetVisBox(bp)
    SetVisBoxForOnOff(bp)
    '''
    # Last Click Rank
    resp_data = []
    sp = 1
    #sp = pos[1]+2
    #pos = [sp, sp+1, sp+2, sp+3]
    pos = [sp, sp+1] 
    #for v in vert:
    for v in ['on','off']:
        print v,'last click', np.median(vertical_stats[v]['last_click'])
        resp_data.append(vertical_stats[v]['last_click'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    #SetVisBox(bp)
    SetVisBoxForOnOff(bp)
    
    # set axes limits and labels
    #plt.xlim(0,pos[3]+1)
    plt.xlim(0,pos[1]+1)
    plt.ylim(0,200)
    plt.ylabel('Time to Click (seconds)')

    ax.set_xticklabels(['Last Click'])#,'Last Click'])
    # ax.set_xticks([2.5, 7.5])
    ax.set_xticks([1.5])#, 4])

    # draw temporary red and blue lines and use them to create a legend
    h1, = plt.plot([1,1],color=vert_color[0])
    h2, = plt.plot([1,1],color=vert_color[1])
    #h3, = plt.plot([1,1],color=vert_color[2])
    #h4, = plt.plot([1,1],color=vert_color[3])
    #plt.legend((h1,h2,h3,h4),verticals, loc='upper center',\
    #    bbox_to_anchor=(0.5, 1.05),ncol=4, fontsize = 12)
    plt.legend((h1,h2),['On','Off'], loc='upper center',\
        bbox_to_anchor=(0.5, 1.05),ncol=2, fontsize = 12)
    h1.set_visible(False)
    h2.set_visible(False)
    #h3.set_visible(False)
    #h4.set_visible(False)

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

def PlotVertSwipeInfoByTime(aggregate_freq, x_title, y_title):
  # Format : {'i': {0 : [] , 1 : [] , 2 : [] .. }}
  # Time buckets are 0 , 1 ,2 .. 10.
  # Each array is fraction of swipes that happen in bucket. 
  i = 0
  face_color = ['lightskyblue','darkgray','lightcoral','palegreen' ]
  edge_color = ['dodgerblue','dimgray','tomato','forestgreen'] 

  for vert_type, bucket_dict in aggregate_freq.items():
      print vert_type, bucket_dict  
      sort_freq = sorted(bucket_dict.items())
      x = []
      mean = []
      var = []
      for entry in sort_freq:
        print entry
        x.append(entry[0])
        mean.append(np.mean(entry[1]))
        var.append(np.std(entry[1]))

      plt.plot(x, mean, 'k', color = vert_color[i], label =\
          vert_expand[vert_type])
      plt.fill_between(x, np.array(mean) - np.array(var), np.array(mean) +\
          np.array(var), alpha=0.2, linewidth=4, linestyle='dashdot',\
          antialiased=True,edgecolor=edge_color[i],\
          facecolor=face_color[i])

      i+=1
  plt.xlabel(x_title)
  plt.ylabel(y_title)
  plt.legend(bbox_to_anchor=(0.5, 1.05), loc='upper center', ncol = 4, fontsize=15)
  plt.show()
  plt.clf()


def PlotMarkovTransitions(vert_state_transitions):
  # Format : {result_type: {state1 : {state2: count}}}

  # Make graph 
  colors = {'start':'lightgreen','end':'salmon','click':'lightyellow','reformulate':'lightblue'}
  for result_type, state_transitions in vert_state_transitions.items():
    #G= nx.MultiDiGraph()
    G = gv.Digraph(format='svg')
    G.graph_attr['layout'] = 'dot'
    states = set([])
    for state1, second_state_dict in state_transitions.items():
      if state1 not in states:
        if state1 in colors:
          G.node(state1,state1,{'style':'filled','fillcolor':colors[state1]})
        else:
          G.node(state1,state1)
      for state2, weight in second_state_dict.items():
        if state2 not in states:
          if state2 in colors:
            G.node(state2,state2,{'style':'filled','fillcolor':colors[state2]})
          else:
            G.node(state2,state2)
        weight=round(weight,2)
        if weight > 0.05:
          G.edge(state1, state2,label=str(weight))
    G.render(result_type+'_trans', view=True) 
    #plt.figure(figsize=(20,10))
    #node_size = 1000
    #pos=nx.circular_layout(G)
    #nx.draw_networkx_edges(G,pos,width=1.0,alpha=0.5)
    #nx.draw_networkx_labels(G, pos, font_weight=2)
    #nx.draw_networkx_edge_labels(G, pos, edge_labels)
    #plt.axis('off');
    #nx.write_dot(G, result_type+'.dot')

    '''val_map = {'start': 1.0,  'end': 1.0, 'swipeup': 0.8, 'swipedown': 0.8,\
        'swipeleft': 0.8, 'swiperight': 0.8, 'reformulate':0.5, 'click':0.3}
    values = [val_map.get(node, 0.25) for node in G.nodes()]
    edge_colors = ['black' for edge in G.edges()]
    pos=nx.circular_layout(G)
    nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels)
    nx.draw(G,pos,node_color = values, node_size=4700,edge_color=edge_colors,edge_cmap=plt.cm.Reds)
    plt.title('Markov transitions for '+vert_expand[result_type])
    nx.write_dot(G, 'mc.dot')
    pylab.show()'''


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
