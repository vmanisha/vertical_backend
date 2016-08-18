import matplotlib.pyplot as plt
import numpy as np
import graphviz as gv

vert = ['i','v','w','o']
verticals = ['Image','Video','Wiki','Organic']
vert_color = ['blue','black','cyan','green']
vert_expand = {'i':'Image','v': 'Video', 'w': 'Wiki', 'o': 'Organic'}

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

plt.rc('font', **font)

def SetVisBox(bp):
  print bp['boxes']
  if len(bp['boxes']) == 4:
    plt.setp(bp['boxes'][0], color=vert_color[0])
    plt.setp(bp['boxes'][1], color=vert_color[1])
    plt.setp(bp['boxes'][2], color=vert_color[2])
    plt.setp(bp['boxes'][3], color=vert_color[3])

def SetVisBoxForOnOff(bp):
    plt.setp(bp['boxes'][0], color=vert_color[0])
    plt.setp(bp['boxes'][1], color=vert_color[1])


'''
@per_vertical_and_pos_data: {vertical_type: {position : [data points]}}
@pos: position to plot results.
@xlabel and @ylabel: Labels for x and y axis respectively.
@title : Plot title
@filename : filename for saving plot.
'''
def PlotMultipleBoxPlotsPerVertical(per_vertical_and_pos_data, doc_pos,\
                                    x_label, y_label,title, filename):
    fig = plt.figure()
    ax = plt.axes()
    plt.hold(True)

    for cid in range(1,doc_pos):
      for v in vert:
        if cid not in per_vertical_and_pos_data[v]:
          per_vertical_and_pos_data[v][cid] = [0]

      time_data = [per_vertical_and_pos_data['i'][cid], \
            per_vertical_and_pos_data['v'][cid],\
            per_vertical_and_pos_data['w'][cid],\
            per_vertical_and_pos_data['o'][cid]]
      sp = ((cid-1)*4)+(cid-1)+1
      pos = [sp, sp+1, sp+2, sp+3]
      print cid, time_data,pos
      # sym='' for not showing outliers
      bp = plt.boxplot(time_data,positions=pos,widths=0.5,sym='')
      # means = [np.mean(data) for data in time_data]
      # ax.plot(pos,means,'rs')
      SetVisBox(bp)

    # set axes limits and labels
    plt.xlim(0,20)
    plt.ylim(0,80)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    ax.set_xticklabels(range(1,doc_pos)) #['1', '2', '3', '4', '5'])
    #ax.set_xticks([2.5, 7.5, 12.5, 17.5, 22.5])
    ax.set_xticks ([x*2.5 for x in range(1,doc_pos*2,2)])
    # draw temporary red and blue lines and use them to create a legend
    h1, = plt.plot([1,1],color=vert_color[0])
    h2, = plt.plot([1,1],color=vert_color[1])
    h3, = plt.plot([1,1],color=vert_color[2])
    h4, = plt.plot([1,1],color=vert_color[3])
    plt.legend((h1,h2,h3,h4),verticals, loc='upper center',\
        bbox_to_anchor=(0.5, 1.05),ncol=2,fontsize=15)
    h1.set_visible(False)
    h2.set_visible(False)
    h3.set_visible(False)
    h4.set_visible(False)

    plt.savefig(filename, bbox_inches='tight' )
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


def PlotSatAndRelBoxPlotPerVertical(first_rel_group, ylabel, filename):
    fig = plt.figure()
    ax = plt.axes()
    plt.hold(True)

    # On Relevance
    resp_data = []
    sp = 1
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
      #resp_data.append(first_rel_group.get_group((v,'relevance'))['response_value'])
      print v, len(first_rel_group.get_group(v)['relevance'])
      resp_data.append(first_rel_group.get_group(v)['relevance'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    SetVisBox(bp)
    
    # On Satisfaction
    resp_data = []
    sp = pos[3]+2
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
      #resp_data.append(first_rel_group.get_group((v,'satisfaction'))['response_value'])
      print v, len(first_rel_group.get_group(v)['satisfaction'])
      resp_data.append(first_rel_group.get_group(v)['satisfaction'])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    SetVisBox(bp)
    
    plt.xlim(0,pos[3]+1)
    plt.ylim(0.5,5.5)
    plt.ylabel(ylabel)

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

    plt.savefig(filename)
    plt.show()


'''
@xlabels : an array of labels to display on x-axis
'''
def PlotVerticalLevelAttributeBoxPlot(vertical_stats, attribute, y_lim, x_labels, y_label, title, filename):
    fig = plt.figure()
    ax = plt.axes()
    plt.hold(True)

    # First Click Rank
    resp_data = []
    sp = 1
    #pos = [sp, sp+1, sp+2, sp+3]
    pos = [sp, sp+1]
    for v in ['on','off']:
    #for v in vert:
        if len(attribute) > 0:
          print v,attribute, vertical_stats[v][attribute]
          resp_data.append(vertical_stats[v][attribute])
        else:
          print v, np.median(vertical_stats[v])
          resp_data.append(vertical_stats[v])

    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    # SetVisBox(bp)
    SetVisBoxForOnOff(bp)
    '''
    
    # Last Click Rank
    resp_data = []
    #sp = pos[1]+2
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
        #print v,'last ranks examined', np.median(vertical_stats[v]['last_rank'])
        #resp_data.append(vertical_stats[v]['last_rank'])
        print v,'last ranks examined', np.median(vertical_stats[v])
        resp_data.append(vertical_stats[v])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    SetVisBox(bp)
    ''' 
    # set axes limits and labels
    plt.xlim(0,pos[1]+1)
    plt.ylim(0,y_lim)
    plt.ylabel(y_label) 

    #ax.set_xticklabels([])#,'Last Click'])
    ax.set_xticklabels(x_labels)
    #ax.set_xticks([2.5, 7.5])
    #ax.set_xticks([1.5])#, 4.5])
    ax.set_xticks([1.5])

    # draw temporary red and blue lines and use them to create a legend
    h1, = plt.plot([1,1],color=vert_color[0])
    h2, = plt.plot([1,1],color=vert_color[1])
    #h3, = plt.plot([1,1],color=vert_color[2])
    #h4, = plt.plot([1,1],color=vert_color[3])
    #plt.legend((h1,h2,h3,h4),verticals, loc='upper center',\
    #    bbox_to_anchor=(0.5, 1.05),ncol=2, fontsize = 15)
    plt.legend((h1,h2),['On','Off'], loc='upper center',\
        bbox_to_anchor=(0.5, 1.05),ncol=2, fontsize = 12)
    h1.set_visible(False)
    h2.set_visible(False)
    #h3.set_visible(False)
    #h4.set_visible(False)

    plt.savefig(filename,bbox_inches='tight' )
    plt.show()


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


def PlotScrollDepthPerVert(highest_card, x_lable, y_label, title,filename):
    fig = plt.figure()
    ax = plt.axes()

    scroll_data = []
    sp = 1
    pos = [sp, sp+1, sp+2, sp+3]
    i=0
    for v in vert:
        scroll_data.append(highest_card[v])
    bp = plt.boxplot(scroll_data,positions=pos,widths=0.5)
    
    # SetVisBox(bp)

    # plt.xlim(0,25)
    plt.ylim(0,10)
    plt.ylabel(y_label)
    ax.set_xticklabels(verticals)

    plt.savefig(filename)
    plt.show()

'''
@attribute1 and @attribute2 : Direction of swipe (up/down, left/right)
@x_ticks: the labels on x-axis, pair of directions (i.e. attr1 and attr2)
'''
def PlotSwipeDataPerVert(swipe_dist, attribute1, attribute2, x_ticks,x_label,\
                        y_label,y_lim, filename):
    fig = plt.figure()
    ax = plt.axes()
    plt.hold(True)

    # PanUp
    resp_data = []
    sp = 1
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
        resp_data.append(swipe_dist[v][attribute1])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    SetVisBox(bp)

    # PanDown
    resp_data = []
    sp = pos[3]+2
    pos = [sp, sp+1, sp+2, sp+3]
    for v in vert:
        resp_data.append(swipe_dist[v][attribute2])
    bp = plt.boxplot(resp_data,positions=pos,widths=0.5)
    SetVisBox(bp)

    plt.xlim(0,pos[3]+1)
    plt.ylim(0,y_lim)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    ax.set_xticklabels(x_ticks)
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

    plt.savefig(filename)
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
  colors = {'start':'green','end':'salmon','click':'lightyellow','reformulate':'lightblue'}
  for result_type, state_transitions in vert_state_transitions.items():
    G = gv.Digraph(format='png')
    G.graph_attr['layout'] = 'dot'
    states = set([])
    for entry in sorted(state_transitions.items()):
      state1= entry[0]
      second_state_dict=entry[1]
      if state1 not in states:
        if state1 in colors:
          G.node(state1,state1,{'style':'filled','fillcolor':colors[state1]})
        else:
          G.node(state1,state1)
      for entry1 in sorted(second_state_dict.items()):
        state2 = entry1[0]
        weight = entry1[1]
        if state2 not in states:
          if state2 in colors:
            G.node(state2,state2,{'style':'filled','fillcolor':colors[state2]})
          else:
            G.node(state2,state2)
        weight=round(weight,2)
        if weight > 0.01 and (state1 in ['start','end'] or\
            state2 in ['start','end']):
          G.edge(state1, state2,label=str(weight))
    G.render(result_type+'_trans', view=True) 


# Format is vert_type : [[x], [y]]
def PlotXYScatter(vert_scatter, x_title, y_title, file_suffix):
  total = []
  probabilities = {}
  for vert_type, xy_points in vert_scatter.items():
    x = np.asarray(xy_points[0])
    y = np.asarray(xy_points[1])
    print vert_type, x, y, len(x), len(y)
    for x1,y1 in zip(xy_points[0],xy_points[1]):
      total.append((x1,y1))
      if x1 not in probabilities:
        probabilities[x1] = {}
      if y1 not in probabilities[x1]:
        probabilities[x1][y1] = 0.0
      probabilities[x1][y1]+=1.0
    fig, ax = plt.subplots()
    fit = np.polyfit(x, y, deg=2)
    ax.plot(x, fit[0] * (x*x) + fit[1]*x + fit[2] , color='red')
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    #plt.xlim(0,11)
    #plt.ylim(0,11)
    plt.xlim(0,max(x)+1)
    plt.ylim(0,max(y)+1)
    ax.scatter(x, y)
    plt.savefig(vert_type+file_suffix,bbox_inches='tight' )
    plt.show()
'''
  sorted_total = sorted(total, key = lambda x: x[0])
  total_x = []
  total_y = []
  for entry in sorted_total:
    total_x.append(entry[0])
    total_y.append(entry[1])

  fig, ax = plt.subplots()
  x = np.asarray(total_x)
  y = np.asarray(total_y)
  fit = np.polyfit(x, y, deg=2)
  ax.plot(x, fit[0] * (x*x) + fit[1]*x + fit[2] , color='red')
  plt.xlabel(x_title)
  plt.ylabel(y_title)
  plt.xlim(0,max(x))
  plt.ylim(0,max(y))
  #plt.xlim(0,11)
  #plt.ylim(0,11)
  ax.scatter(x, y)
  plt.savefig('total_scatter_click_time.png',bbox_inches='tight' )
  plt.show()
  
  confusion_matrix = []
  for rank1 in range(11):
    row = []
    total = 0.0
    if rank1 in probabilities:
      total = sum(probabilities[rank1].values())
    for rank2 in range(11):
      if rank1 in probabilities and rank2 in probabilities[rank1]:
        row.append(probabilities[rank1][rank2]/total)
      else:
        row.append(0)
    confusion_matrix.append(row)

  fig = plt.figure()
  plt.clf()
  ax = fig.add_subplot(111)
  ax.set_aspect(1)
  res = ax.imshow(np.array(confusion_matrix), cmap=plt.cm.jet, 
                  interpolation='nearest')
  
  for x in xrange(11):
      for y in xrange(11):
          ax.annotate(str(round(confusion_matrix[x][y],2)), xy=(y, x), 
                      horizontalalignment='center',
                      verticalalignment='center')
  
  cb = fig.colorbar(res)
  plt.xlabel(x_title)
  plt.ylabel(y_title)
  plt.show()
  plt.savefig('confusion_matrix.png', format='png')
'''

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
