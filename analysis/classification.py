
import pandas as pd
import numpy as np
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import StratifiedKFold
from sklearn.metrics import roc_curve, auc, confusion_matrix
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
from scipy import interp
import matplotlib.pyplot as plt

def CorrelationAndClassification(features):
    # write to another file.
    remaining_features = features.drop(['first_event_time','first_result_time',\
             'last_event_time'], axis =1)
    remaining_features.to_csv('serp_features_clean.csv',index=False,encoding='utf-8')

    remaining_features = remaining_features.reset_index()
    # get satisfaction and relevance labels 
    satisfaction = remaining_features['satisfaction'].map({1:0,2:0, 3:0, 4:1,5:1 })
    print satisfaction.value_counts()
    print satisfaction.shape
    relevance = remaining_features['relevance']

    # take every column and find set all other values to 0. 
    remaining_features = remaining_features.drop(['relevance','satisfaction',\
            'query_task'], axis =1)
    # Merge the features : (tap and double tap)
    remaining_features = remaining_features.drop(['index'], axis = 1)
    remaining_features = remaining_features.fillna(0)

    # map the vertical name to number.
    remaining_features['vert_sess_result_type'] =\
            remaining_features['vert_sess_result_type'].map({'i':1, 'v':2, 'w':3, 'o':4})
    
    # Normalize the features
    remaining_features = (remaining_features - remaining_features.mean()) \
            / (remaining_features.max() - remaining_features.min())
    feature_groups = GetFeatureGroups(remaining_features)

    for group_name, feat_list in feature_groups.items():
      # Convert the features into lists. 
      features_list = remaining_features[feat_list].values.tolist()
      for c in [1,2, 10, 50]:
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
          print c, group_name, np.mean(all_prec), np.mean(all_recall), np.mean(all_accuracy)
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
          plt.show()
          #plt.clf()


def GetFeatureGroups(data_frame):
  ftype =['gest','vert','view','cq']
  groups = {'all_feat':[]}

  for gtype in ftype:
    if gtype not in groups:
      groups[gtype+'_pc'] = []
      groups[gtype+'_all'] = []
      groups[gtype+'_sess'] = []


  for feat in data_frame.columns:
    groups['all_feat'].append(feat)
    if 'fr' in feat:
      groups['vert_all'].append(feat)
      if 'pc' in feat:
        groups['vert_pc'].append(feat)
      if 'sess' in feat:
        groups['vert_sess'].append(feat)
    else:
      for gtype in ftype:
        if gtype in feat:
          groups[gtype+'_all'].append(feat)
          if 'pc' in feat:
            groups[gtype+'_pc'].append(feat)
          if 'sess' in feat:
            groups[gtype+'_sess'].append(feat)


  for gname, glist in groups.items():
    print gname, glist

  return groups


