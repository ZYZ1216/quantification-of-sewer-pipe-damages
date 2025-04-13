import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# The first code fragment - Appears in 'Basic Data Summary and Structure'
df = pd.read_csv('path_to_metadata.csv')
print(df.describe())
print(df.info())
print(df.isnull().sum())
print(df['class'].value_counts())


# Class Distribution (Fault Types) plot (plot_1.png) 
plt.figure(figsize=(10,6))
sns.countplot(data=df, x='class')
plt.xticks(rotation=45)
plt.title('Class Distribution of Fault Types')
plt.show()


# Bounding Box Analysis (plot_2.png)
df['bbox_width'] = df['xmax'] - df['xmin']
df['bbox_height'] = df['ymax'] - df['ymin']
plt.figure(figsize=(10,6))
sns.histplot(df['bbox_width'], kde=True, color='blue', label='Width')
sns.histplot(df['bbox_height'], kde=True, color='red', label='Height')
plt.legend()
plt.title('Distribution of Bounding Box Sizes (Width and Height)')
plt.show()


# Aspect Ratio of bounding boxes (plot_3.png)
df['bbox_aspect_ratio'] = df['bbox_width'] / df['bbox_height']
plt.figure(figsize=(10,6))
sns.histplot(df['bbox_aspect_ratio'], kde=True, color='green')
plt.title('Bounding Box Aspect Ratio Distribution')
plt.show()


# Fault Localization within Images (Heatmap) (plot_4.png)
df['bbox_center_x'] = (df['xmin'] + df['xmax']) / 2
df['bbox_center_y'] = (df['ymin'] + df['ymax']) / 2
plt.figure(figsize=(10,6))
sns.kdeplot(data=df, x='bbox_center_x', y='bbox_center_y', cmap='Blues', shade=True)
plt.title('Density of Faults in Image Space (Bounding Box Centers)')
plt.show()


# Correlation Analysis Between Faults and Bounding Box Sizes (Box plots) (plot_5.png and plot_6.png)
# for width
sns.boxplot(data=df, x='class', y='bbox_width')
plt.xticks(rotation=45)
plt.title('Bounding Box Width by Fault Class')
plt.show()
# for height
sns.boxplot(data=df, x='class', y='bbox_height')
plt.xticks(rotation=45)
plt.title('Bounding Box Height by Fault Class')
plt.show()