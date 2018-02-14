from sklearn import svm
import sklearn.metrics as smet
from sklearn.metrics import roc_curve
import matplotlib.pyplot as plt
from sklearn.multiclass import OneVsOneClassifier
import nltk
from nltk import pos_tag
from nltk.corpus import stopwords
import numpy as np
import matplotlib.pyplot as plt
from pickle import dump
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from string import punctuation
from nltk.stem.snowball import SnowballStemmer
import string
import re
from scipy.sparse.linalg import svds
from sklearn.decomposition import TruncatedSVD

from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_curve
from sklearn.metrics import auc

from sklearn.pipeline import Pipeline
import itertools

snowball_stemmer = SnowballStemmer("english")
analyzer = CountVectorizer().build_analyzer()
tfidf_transform = TfidfTransformer()



def stemTokenizer (doc) :
	doc = re.sub('[,.-:/()?{}*$#&]', ' ', doc)
	doc = ''.join(ch for ch in doc if ch not in string.punctuation)
	doc = ''.join(ch for ch in doc if ord(ch) < 128)
	doc = doc.lower()
	words = doc.split()
	words = [word for word in words if word not in text.ENGLISH_STOP_WORDS]

	return [snowball_stemmer.stem(word) for word in words]

classCategories = ['comp.sys.ibm.pc.hardware', 'comp.sys.mac.hardware', 'misc.forsale', 'soc.religion.christian']


twenty_train = fetch_20newsgroups(subset='train', categories=classCategories, shuffle=True, random_state=42,)
twenty_test = fetch_20newsgroups(subset='test', categories=classCategories, shuffle=True, random_state=42,)


count_vect1 = CountVectorizer(min_df=5,max_df=0.99, tokenizer=stemTokenizer)
# X_train_counts1 = count_vect1.fit_transform(twenty_train.data)
# X_train_tfidf = tfidf_transform.fit_transform(X_train_counts1)

# X_test_counts1 = count_vect1.transform(twenty_test.data)
# X_test_tfidf = tfidf_transform.transform(X_test_counts1)


# uTrain, sTrain, vtTrain = svds(X_train_tfidf.toarray(), k=50)
# uTest, sTest, vtTest = svds(X_test_tfidf.toarray(), k=50)

train_target_group = twenty_train.target
test_target_group = twenty_test.target

penalties = [0.001, 1, 1000]

# def plot_roc(fpr, tpr, C):

# 	plt.figure()

# 	fig, ax = plt.subplots()

# 	roc_auc = auc(fpr, tpr)

# 	ax.plot( fpr, tpr, lw=2, label= 'area under curve = %0.4f' % roc_auc)

# 	ax.grid(color='0.7', linestyle='--', linewidth=1)
# 	plt.title("ROC curve for SVM Classifier")
# 	ax.set_xlim([-0.1, 1.1])
# 	ax.set_ylim([0.0, 1.05])
# 	ax.set_xlabel('False Positive Rate',fontsize=15)
# 	ax.set_ylabel('True Positive Rate',fontsize=15)

# 	ax.legend(loc="lower right")

# 	for label in ax.get_xticklabels()+ax.get_yticklabels():
# 	    label.set_fontsize(15)
# 	plt.savefig("svmSVDRoc" + str(C) + ".png")

def print_statistics(actual, predicted):
    print "Accuracy is ", smet.accuracy_score(actual, predicted) * 100
    print "Precision is ", smet.precision_score(actual, predicted, average='macro') * 100

    print "Recall is ", smet.recall_score(actual, predicted, average='macro') * 100

    print "Confusion Matrix is ", smet.confusion_matrix(actual, predicted)

def get_svd():
    return TruncatedSVD(n_components=50)


def fetchLSIRepresentation(pipeline, train, test):
	svd_matrix_train = pipeline.fit_transform(train.data)
	svd_matrix_test = pipeline.transform(test.data)
	return svd_matrix_train, svd_matrix_test



def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    plt.figure()
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=90)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.savefig("cf"+str(normalize) + ".png")


pipeline1 = Pipeline([
    ('vect', CountVectorizer(min_df=5, stop_words=text.ENGLISH_STOP_WORDS)),
    ('tfidf', TfidfTransformer()),
    ('reduce_dim', get_svd()),
])

train_lsi, test_lsi = fetchLSIRepresentation(pipeline1, twenty_train,  twenty_test)

ovo_svc = OneVsOneClassifier(svm.SVC(kernel='linear', probability=True, C = 1000))


ovo_svc.fit(train_lsi, train_target_group)
predicted = ovo_svc.predict(test_lsi)
print_statistics(test_target_group, predicted)

predicted_probs = ovo_svc.decision_function(test_lsi)

#fpr, tpr, _ = roc_curve(test_target_group, predicted_probs)

#plot_roc(fpr, tpr, penalty)

cnf_matrix = smet.confusion_matrix(test_target_group, predicted)
plot_confusion_matrix(cnf_matrix, classes=classCategories, title='Multiclass Confusion matrix')
#plot_confusion_matrix(cnf_matrix, classes=classCategories, normalize=True, title='Confusion matrix with normalization' )



