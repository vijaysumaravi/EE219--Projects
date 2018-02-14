# K means for all combined data of all 8 categories grouped into two classes. 

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
import itertools
from sklearn import metrics
from sklearn.cluster import KMeans, MiniBatchKMeans

from sklearn.preprocessing import StandardScaler
from numpy import *
from numpy import ma
from sklearn.decomposition import NMF
from scipy.sparse.linalg import svds
from sklearn.decomposition import TruncatedSVD

snowball_stemmer = SnowballStemmer("english")
analyzer = CountVectorizer().build_analyzer()
tfidf_transform = TfidfTransformer()



# def stemTokenizer (doc) :
# 	doc = re.sub('[,.-:/()?{}*$#&]', ' ', doc)
# 	doc = ''.join(ch for ch in doc if ch not in string.punctuation)
# 	doc = ''.join(ch for ch in doc if ord(ch) < 128)
# 	doc = doc.lower()
# 	words = doc.split()
# 	words = [word for word in words if word not in text.ENGLISH_STOP_WORDS]

# 	return [snowball_stemmer.stem(word) for word in words]

def printConfusionMatrix(actual, predicted):
    print "-" * 20
    print "Confusion Matrix is ", metrics.confusion_matrix(actual, predicted)
    print "-" * 20



def printScores(actual_labels, predicted_labels):
    
    print "-" * 20
    print("Homogeneity: %0.3f" % metrics.homogeneity_score(actual_labels, predicted_labels))
    print("Completeness: %0.3f" % metrics.completeness_score(actual_labels, predicted_labels))
    print("Adjusted Rand-Index: %.3f" % metrics.adjusted_rand_score(actual_labels, predicted_labels))
    print("V-measure: %0.3f" % metrics.v_measure_score(actual_labels, predicted_labels))
    print("Adjusted Mutual info score: %.3f" % metrics.adjusted_mutual_info_score(actual_labels, predicted_labels))
    print "-" * 20

def plotConfusionMatrix(cm, classes,
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
    plt.savefig("confusionMatrix.png", format='png')






computerClass = ['comp.graphics', 'comp.os.ms-windows.misc', 'comp.sys.ibm.pc.hardware', 'comp.sys.mac.hardware']
recreationClass = ['rec.autos', 'rec.motorcycles', 'rec.sport.baseball', 'rec.sport.hockey']
classCategories = ['Computer Technology', 'Recreation Activity']

# class_1 = fetch_20newsgroups(subset = 'all', categories = computerClass, shuffle=True, random_state=42);
# class_2 = fetch_20newsgroups(subset = 'all', categories = recreationClass, shuffle=True, random_state=42);

total = fetch_20newsgroups(subset = 'all', categories = computerClass+recreationClass, shuffle=True, random_state=42);

		


count_vect1 = CountVectorizer(min_df=3, stop_words='english')


# class_1_Count = count_vect1.fit_transform(class_1.data)
# class_1_tfidf = tfidf_transform.fit_transform(class_1_Count)
# print "Number of terms in class1 data TF-IDF representation:",class_1_tfidf.shape

# class_2_Count = count_vect1.fit_transform(class_2.data)
# class_2_tfidf = tfidf_transform.fit_transform(class_2_Count)
# print "Number of terms in class2 data TF-IDF representation:",class_2_tfidf.shape

totalCount = count_vect1.fit_transform(total.data)
totalData_tfidf = tfidf_transform.fit_transform(totalCount)
#print "Number of terms in combined data TFxIDF representation:",totalData_tfidf.shape

labels = [ int(x / 4) for x in total.target]



nmf = NMF(n_components=2, init = 'random', random_state=0)
totalNMF = nmf.fit_transform(totalData_tfidf)

scaler = StandardScaler(with_mean=False, with_std=True)
normData = scaler.fit_transform(totalNMF)

normData += 0.1
logData = np.log(normData)

kmeans = KMeans(n_clusters=2, n_init=30).fit(logData)

printConfusionMatrix(labels, kmeans.labels_)
printScores(labels, kmeans.labels_)

cm = metrics.confusion_matrix(labels, kmeans.labels_)


classCategories = ['Recreation Activity', 'Computer Technology']
plotConfusionMatrix(cm,  classes=classCategories, title='Confusion matrix')





x1 = logData[kmeans.labels_ == 0][:, 0]
y1 = logData[kmeans.labels_ == 0][:, 1]

plt.figure()
plt.plot(x1,y1,'g+')
x2 = logData[kmeans.labels_ == 1][:, 0]
y2 = logData[kmeans.labels_ == 1][:, 1]

plt.plot(x2, y2, 'r+')
plt.title("2D Projection of Feature Vectors ")


plt.savefig("clusterslog2dNMF.png", format='png')













