import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn import cluster
from sklearn.cluster import KMeans
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

#################################################################################################################################################
#################################################################################################################################################

game_limit = 10
with open('feature_over_' + str(game_limit) + '.json', "r") as json_file:
    data = json.load(json_file)

row_indices = [d[0] for d in data]
col_names = ['kills', 'deaths', 'assists', 'champlevel', 'totaldamagedealt', 
'totaldamagedealttochampions', 'damagedealttoobjectives', 'damagedealttoturrets', 'totaldamagetaken', 'neutralminionskilledteamjungle', 
'neutralminionskilledenemyjungle', 'neutralminionskilled', 'totalminionskilled', 'goldearned', 'goldspent', 
'wardsplaced', 'wardskilled', 'visionwardsboughtingame', 'visionscore']

data = [d[1:] for d in data]
dataframe = pd.DataFrame(data, index=row_indices, columns=col_names)

#################################################################################################################################################
#################################################################################################################################################

# Feature scaling for all features
for col in col_names:
    MIN, MAX = min(dataframe[col]), max(dataframe[col])
    for i in range(len(dataframe[col])):
        dataframe[col][i] = round((dataframe[col][i] - MIN) / (MAX - MIN), 5)

#################################################################################################################################################
#################################################################################################################################################

# # find inertia value for all features
# inertias = []
# for k in range(1,10):
#     model = KMeans(n_clusters=k)
#     model.fit(dataframe)
#     inertias.append(model.inertia_)
# plt.plot(range(1,10), inertias, '-o')
# plt.xlabel('number of clusters')
# plt.ylabel('inertia')
# plt.xticks(range(1,10))
# plt.show()

#################################################################################################################################################
#################################################################################################################################################

# # Execute K-means for all features
# model = KMeans(n_clusters=3)
# model.fit(dataframe)
# dataframe['cluster'] = model.labels_
# print(model.cluster_centers_)
# centroids = []
# for centroid in model.cluster_centers_:
#     centroid_dict = {}
#     for i in range(len(col_names)):
#         centroid_dict[col_names[i]] = round(centroid[i], 5)
#     centroids.append(centroid_dict)
# print(centroids)

# # plot
# sns.scatterplot(x = 'neutralminionskilled', y = 'totalminionskilled', data=dataframe, hue='cluster')
# plt.show()

#################################################################################################################################################
#################################################################################################################################################

# Execute K-means for all features
model = KMeans(n_clusters=3)
model.fit(dataframe)
dataframe['cluster'] = model.labels_
print(model.cluster_centers_)
centroids = []
for centroid in model.cluster_centers_:
    centroid_dict = {}
    for i in range(len(col_names)):
        centroid_dict[col_names[i]] = round(centroid[i], 5)
    centroids.append(centroid_dict)
print(centroids)

select_cluster = 0
for i in range(len(centroids)):
    if centroids[i]['totaldamagedealttochampions'] > centroids[select_cluster]['totaldamagedealttochampions']:
        select_cluster = i

cluster_ = dataframe[dataframe['cluster'] == select_cluster]
feature = cluster_[col_names]

# # find inertia value for cluster
# inertias = []
# for k in range(1,10):
#     model = KMeans(n_clusters=k)
#     model.fit(cluster_1)
#     inertias.append(model.inertia_)
# plt.plot(range(1,10), inertias, '-o')
# plt.xlabel('number of clusters')
# plt.ylabel('inertia')
# plt.xticks(range(1,10))
# plt.show()

# Execute K-means for cluster
model = KMeans(n_clusters=5)
model.fit(feature)
feature['new_cluster'] = model.labels_
print(model.cluster_centers_)
centroids = []
for centroid in model.cluster_centers_:
    centroid_dict = {}
    for i in range(len(col_names)):
        centroid_dict[col_names[i]] = round(centroid[i], 5)
    centroids.append(centroid_dict)
print(centroids)

# plot
sns.scatterplot(x = 'deaths', y = 'totaldamagedealttochampions', data=feature, hue='new_cluster')
plt.show()

#################################################################################################################################################
#################################################################################################################################################

selected_features = ['kills', 'deaths', 'assists', 'totaldamagedealt', 'totaldamagedealttochampions', 'totaldamagetaken']
feature = dataframe[selected_features]

#################################################################################################################################################
#################################################################################################################################################

# # find inertia value for selected features
# inertias = []
# for k in range(1,10):
#     model = KMeans(n_clusters=k)
#     model.fit(feature)
#     inertias.append(model.inertia_)
# plt.plot(range(1,10), inertias, '-o')
# plt.xlabel('number of clusters')
# plt.ylabel('inertia')
# plt.xticks(range(1,10))
# plt.show()

#################################################################################################################################################
#################################################################################################################################################

# # Execute K-means for selected features
# model = KMeans(n_clusters=3)
# model.fit(feature)
# feature['cluster'] = model.labels_
# print(model.cluster_centers_)
# centroids = []
# for centroid in model.cluster_centers_:
#     centroid_dict = {}
#     for i in range(len(selected_features)):
#         centroid_dict[selected_features[i]] = round(centroid[i], 5)
#     centroids.append(centroid_dict)
# print(centroids)

# # plot
# sns.scatterplot(x = 'deaths', y = 'totaldamagedealttochampions', data=feature, hue='cluster')
# plt.show()