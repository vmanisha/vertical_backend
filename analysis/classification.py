from scipy.stats import ttest_ind
import pandas as pd
import numpy as np
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import StratifiedKFold
from sklearn.metrics import roc_curve, auc, confusion_matrix
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
from scipy import interp
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

def ComputeFeatMeanStdDevOfSatAndDSatLabels(remaining_features):
    
    # Find the mean and std-dev of each feature for SAT and DSAT SERP. 
    remaining_features = remaining_features[\
              remaining_features['vert_sess_result_type'] ==1]

    for feat in remaining_features.columns:
      if feat not in ['relevance', 'query_task', 'satisfaction']:
        # Get two groups of SAT and DSAT label and print mean, std-dev and
        # welch t-test value. 
        groups =  remaining_features[feat].groupby(remaining_features['satisfaction'])
        means = groups.mean()
        stds = groups.std()
        print feat, 'mean ', means.ix[0], stds.ix[0], means.ix[1] ,\
          stds.ix[1],ttest_ind(groups.get_group(1), groups.get_group(0))



def PerformClassificationViaCrossValidation(remaining_features, satisfaction, result_file):
    remaining_features = remaining_features.drop(['relevance','satisfaction',\
            'query_task'], axis =1)
    # Normalize the features
    remaining_features = (remaining_features - remaining_features.mean()) \
            / (remaining_features.max() - remaining_features.min())
    feature_groups = GetFeatureGroups(remaining_features)
    group_metrics = {}

    for group_name, feat_list in feature_groups.items():
      # Convert the features into lists. 
      features_list = remaining_features[feat_list].values.tolist()
      for c in [1]:
          mean_tpr = 0.0
          mean_fpr = np.linspace(0, 1, 100)
          all_tpr = []
          all_prec = []
          all_recall = []
          all_accuracy = []
          confusion_matrix_total = {}
          # Predict Satisfaction using Logistic regression and print auc.
          for k, (train, test) in enumerate(StratifiedKFold(satisfaction, 5)):
              x_train = [ features_list[i] for i in train]
              y_train = satisfaction.loc[train]
              x_test = [ features_list[i] for i in test]
              y_test = satisfaction[test]

              clf = LogisticRegression(C=c, penalty='l1')
              clf_fit = clf.fit(x_train, y_train)
              coeff = clf_fit.coef_.ravel()
              coeff_tuple = []
              
              for i in range(len(feat_list)):
                  coeff_tuple.append((feat_list[i],round(coeff[i],5)))
              for ctuple in coeff_tuple:
                  print group_name, 'fold',k,'c', c, ctuple[0], ctuple[1]

              # Get the confusion matrices. 
              y_predict= clf_fit.predict(x_test)
              kprec, krecall , f , s= precision_recall_fscore_support(y_test, y_predict)
              all_prec.append(kprec)
              all_recall.append(krecall)
              all_accuracy.append(accuracy_score(y_test, y_predict))

              confusion_fold = confusion_matrix(y_test, y_predict)
              for i in range(len(confusion_fold)):
                  total = sum(confusion_fold[i])
                  if i not in confusion_matrix_total:
                      confusion_matrix_total[i] = {}
                  for j in range(len(confusion_fold)):
                      if j not in confusion_matrix_total[i]:
                          confusion_matrix_total[i][j] = 0.0
                      confusion_matrix_total[i][j] += (confusion_fold[i][j] *1.0)/total 
              
              prob_y_test = clf_fit.predict_proba(x_test)
              fpr, tpr, thresholds = roc_curve(y_test, prob_y_test[:, 1])
              mean_tpr += interp(mean_fpr, fpr, tpr)
              mean_tpr[0] = 0.0
              roc_auc = auc(fpr, tpr)
              plt.plot(fpr, tpr, lw=1, label='ROC fold %d (area = %0.2f)' % (k,
                  roc_auc))

          for i, jdict in confusion_matrix_total.items():
              for j,value in jdict.items():
                  print 'logistic c=',c,i,j,value/5

          plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Random')
          mean_tpr /= 5  # Number of folds. 
          mean_tpr[-1] = 1.0
          mean_auc = auc(mean_fpr, mean_tpr)
          group_metrics[group_name+'_'+str(c)] = {'prec':np.mean(all_prec),\
              'recall':np.mean(all_recall), 'accuracy':np.mean(all_accuracy),\
              'auc':mean_auc}
          print str(c), group_name, group_metrics[group_name+'_'+str(c)]
          plt.plot(mean_fpr, mean_tpr, 'k--',
                           label='Mean ROC (area = %0.2f)' % mean_auc, lw=2)

          plt.xlim([-0.05, 1.05])
          plt.ylim([-0.05, 1.05])
          plt.xlabel('False Positive Rate')
          plt.ylabel('True Positive Rate')
          plt.title('Receiver operating characteristic Logistic C='+str(c))
          #plt.legend(loc="lower right")
          plt.legend(loc='lower right', ncol = 1, fontsize=15)
          plt.savefig(group_name+'_roc_logistic_'+str(c)+'.png',bbox_inches='tight')
          #plt.show()
          plt.clf()
    metric_dataframe = pd.DataFrame.from_dict(group_metrics)
    metric_dataframe.to_csv(result_file)

def PrepareFeaturesAndSatisfactionLabels(features, clean_feat_file):
    
    # Get the first click rank between tap and click rank.
    features['cq_sess_fcr'] = features[['cq_sess_ftr',\
                                                         'cq_sess_fcr']].min(axis=1)
    # Get the session time. 
    features['cq_sess_time'] = features['last_event_time']

    # Remove first tap rank, first and last event and result time column
    remaining_features = features.drop(['first_event_time','first_result_time',\
             'last_event_time', 'cq_sess_ftr', 'gest_sess_td'], axis =1)

    # write to another file.
    remaining_features.to_csv(clean_feat_file,index=False,encoding='utf-8')
    
    remaining_features = remaining_features.reset_index()
    
    # get satisfaction and relevance labels 
    remaining_features['satisfaction'] = remaining_features['satisfaction'].map({1:0,2:0, 3:0, 4:1,5:1 })
    satisfaction = remaining_features['satisfaction']

    print 'Satisfaction dist',satisfaction.value_counts()
    print 'Satisfaction shape',satisfaction.shape
    # Fill NAs with 0. 
    remaining_features = remaining_features.fillna(0)

    relevance = remaining_features['relevance']

    remaining_features['gest_pc_ast'] = remaining_features[['gest_pc_time_list_sl',\
            'gest_pc_time_list_sr','gest_pc_time_list_sd',\
            'gest_pc_time_list_su']].mean(axis=1)
    
    remaining_features['gest_sess_ast'] = remaining_features[[\
            'gest_sess_time_list_sl', 'gest_sess_time_list_sr',\
            'gest_sess_time_list_sd','gest_sess_time_list_su']].mean(axis=1)
    
    remaining_features = remaining_features.drop([\
        'gest_pc_time_list_su','gest_pc_time_list_sd',\
            'gest_sess_time_list_sl', 'gest_sess_time_list_sr',\
            'gest_sess_time_list_su','gest_sess_time_list_sd',\
            'gest_pc_time_list_sl', 'gest_pc_time_list_sr'],axis=1)
    '''
    remaining_features['gest_sess_h_fsw_time'] = remaining_features[['gest_sess_fsl_time',\
            'gest_sess_fsr_time']].mean(axis=1)
    remaining_features['gest_sess_v_fsw_time'] = remaining_features[['gest_sess_fsd_time',\
            'gest_sess_fsu_time']].mean(axis=1)
    
    remaining_features = remaining_features.drop(['gest_sess_fsd_time',\
        'gest_sess_fsu_time','gest_pc_time_list_su','gest_pc_time_list_sd',\
            'gest_sess_fsl_time', 'gest_sess_fsr_time',\
            'gest_sess_time_list_sl', 'gest_sess_time_list_sr',\
            'gest_sess_time_list_su','gest_sess_time_list_sd',\
            'gest_pc_time_list_sl', 'gest_pc_time_list_sr'],axis=1)
    '''
    # Merge the features : (tap and double tap)
    remaining_features = remaining_features.drop(['index'], axis = 1)
    
    # map the vertical name to number.
    remaining_features['vert_sess_result_type'] =\
            remaining_features['vert_sess_result_type'].map({'i':1, 'v':2, 'w':3, 'o':4})
    
    remaining_features.to_csv('serp_features_for_r.csv',index=False,encoding='utf-8')

    return remaining_features, satisfaction
    
def ComputeCorrelations(remaining_features):
    # Take all columns and print pearson corr
    organic_satisfaction = remaining_features[remaining_features['vert_sess_result_type'] ==\
                                            4]['satisfaction']
    print 'image sat dist',organic_satisfaction.value_counts()
    print 'image shape',organic_satisfaction.shape
    # take every column and find set all other values to 0. 
    organic_features=remaining_features[remaining_features['vert_sess_result_type']== 4]
    
    for entry in remaining_features.columns:
        pearson, pval = pearsonr(organic_features[entry], organic_satisfaction)
        if pval < 0.1:
            print entry,pearson, pval

def GetFeatureGroups(data_frame):
  ftype =['gest','vert','view','cq']
  groups = {'all_all_feat':[]} #,'all_pc_feat':[], 'all_sess_feat':[]}

  for gtype in ftype:
    if gtype not in groups:
      #groups[gtype+'_pc'] = []
      groups[gtype+'_all'] = []
      #groups[gtype+'_sess'] = []

  for feat in data_frame.columns:
    groups['all_all_feat'].append(feat)
    if 'fr' in feat:
      groups['vert_all'].append(feat)
      '''if 'pc' in feat:
        groups['vert_pc'].append(feat)
      if 'sess' in feat:
        groups['vert_sess'].append(feat)'''
    else:
      for gtype in ftype:
        if gtype in feat:
          groups[gtype+'_all'].append(feat)
          '''if 'pc' in feat:
            groups[gtype+'_pc'].append(feat)
            groups['all_pc_feat'].append(feat)
          if 'sess' in feat:
            groups[gtype+'_sess'].append(feat)
            groups['all_sess_feat'].append(feat)'''
  
  names = groups.keys()
  for i in range(len(names)):
      if names[i] not in ['all_all_feat', 'all_pc_feat', 'all_sess_feat']:
        for j in range(i+1,len(names)):
            if names[j] not in ['all_all_feat', 'all_pc_feat', 'all_sess_feat']:
                if ('all' in names[i] and 'all' in names[j]) or \
                   ('pc' in names[i] and 'pc' in names[j]) or \
                   ('sess' in names[i] and 'sess' in names[j]):
                    groups[names[i]+'_'+names[j]] = groups[names[i]] + groups[names[j]]

  # Merge groups
  groups['cq_all_vert_all_gest_all'] = groups['cq_all_vert_all'] +\
  groups['gest_all'] #no view
  groups['view_all_vert_all_gest_all'] = groups['gest_all_vert_all'] +\
  groups['view_all'] # no cq
  groups['cq_all_vert_all_view_all'] = groups['cq_all_vert_all'] +\
  groups['view_all']# no gest
  groups['cq_all_view_all_gest_all'] = groups['cq_all_view_all'] +\
  groups['gest_all'] #no vert

  for gname, glist in groups.items():
    print gname, glist

  return groups


