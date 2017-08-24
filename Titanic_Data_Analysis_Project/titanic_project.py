# -*- coding: utf-8 -*-
 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Reading the Titanic data file
data = pd.read_csv('C:/Users/Subash Bharadwaj/Desktop/titanic-data.csv')

# Data Cleanup - Replacing all 'NaN' Cabin names with blank values
data.Cabin = data.Cabin.fillna('')

# Data Cleanup - Split the data into two groups (one with data on age, one with age data missing)
data_agemissing = data[pd.isnull(data).Age]
data_notmissing = data[pd.notnull(data).Age]

# First Figure
plt.figure(1)
plt.title('Age Distribution of the Population')
plt.xlabel('Age Brackets')
# Bins for the age histogram
bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
# Histogram of Age distribution
data_notmissing['Age'].plot.hist(bins)
# Positively skewed distribution
print 'Mean age of passegners is:' + str(data_notmissing['Age'].mean())
print 'Median age of passegners is:' + str(data_notmissing['Age'].median())
# Overlapping Histogram of Age distribution for individuals who are alone
data_notmissing['Age'][(data_notmissing['SibSp']==0) & (data_notmissing['Parch']==0)].plot.hist(bins)
# Positively skewed distribution
print 'Mean age of lone passegners is:' + str(data_notmissing['Age'][(data_notmissing['SibSp']==0) & (data_notmissing['Parch']==0)].mean())
print 'Median age of lone passegners is:' + str(data_notmissing['Age'][(data_notmissing['SibSp']==0) & (data_notmissing['Parch']==0)].median())
# Second Figure
plt.figure(2)
plt.title('Survival Rate by Sex & Class')
plt.ylabel('Survival Rate in %')
# Survival Rate by Sex and by Ticket Class - use full data
(data.groupby(['Sex', 'Pclass'])['Survived'].sum()/data.groupby(['Sex', 'Pclass'])['Survived'].count()*100).plot.bar()
# Function to split the age data into age cohorts
def age_cohort(age):
    if age<=18:
        cohort = 'Upto 18 Years'
    elif age>18 and age<=30:
        cohort = '18-30 Years'
    elif age>30 and age<=60:
        cohort = '30-60 Years'
    else:
        cohort = 'Over 60 Years'
    return cohort
#Apply method to convert the age data into age cohorts
data_notmissing['Age_Cohort'] = data_notmissing['Age'].apply(age_cohort)
# Third Figure
plt.figure(3)
plt.title('Survival Rate by Age Cohort')
plt.ylabel('Survival Rate in %')
# Survival Rate by Age Cohort
(data_notmissing.groupby('Age_Cohort')['Survived'].sum()/data_notmissing.groupby('Age_Cohort')['Survived'].count()*100).plot.bar()
