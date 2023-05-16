import pandas as pd
from matplotlib import pyplot as plt 
import requests
from bs4 import BeautifulSoup
import seaborn as sns
from selenium import webdriver
import re

#apply desired filters on website, enter link of first page below
url_base = 'https://www.autotrader.com/cars-for-sale/all-cars/cars-between-6500-and-21999/blackwood-nj?requestId=SEDAN&maxMileage=100000&makeCodeList=HONDA%2CTOYOTA%2CAUDI&searchRadius=50&zip=08012&startYear=2010&marketExtension=include&vehicleStyleCodes=COUPE%2CSEDAN&isNewSearch=true&showAccelerateBanner=false&sortBy=relevance&numRecords=25'
first_record = list(range(25,500,25))

#get urls from multiple pages since each page is limited to showing only 25 cars
url_list = []
for increment in first_record:
    urlnew = url_base + "&firstRecord=" + str(increment)
    url_list.append(urlnew)

#function to create df
def create_df(completelist):
    df = pd.DataFrame()
    
    for url in completelist:
        result = requests.get(url)
        soup = BeautifulSoup(result.text, 'html.parser')
        
        layer_titles = soup.find_all('div', class_ = 'display-flex justify-content-between')
        layer_prices = soup.find_all('div', class_ = 'text-gray-base text-bold text-size-500' )
        layer_mileages = soup.find_all('div', class_ = 'item-card-specifications col-xs-9 margin-top-4 text-subdued-lighter')

        titles = []
        for item in layer_titles:
            name = item.h3.text
            titles.append(name)
            
        prices=[]
        for item in layer_prices:
            price = item.span.text
            prices.append(price)
            
        mileage=[]
        for item in layer_mileages:
            mileagevalue = item.span.text
            mileage.append(mileagevalue)
        
        titles = titles[2:]
        prices = prices[2:]
        mileage = mileage[2:]
        
        x = {'title': titles, 'price': prices, "mileage":mileage}
        df = pd.concat([df, pd.DataFrame(x)], ignore_index=True)
    return df

df = create_df(url_list)

#convert mileage and price columns into int
remove_non_numeric = lambda x: re.sub('\D', '', str(x))
df['mileage'] = df['mileage'].apply(remove_non_numeric)
df['mileage'] = df['mileage'].astype(int)

df['price'] = df['price'].apply(remove_non_numeric)
df['price'] = df['price'].astype(int)
df.sort_values(by = "price", inplace=True)

#extract year 
df['year'] = df['title'].apply(remove_non_numeric).str[:4]
df['year'] = df['year'].astype(int)
df.info()
df['make'].value_counts()

df['make'] = pd.Series()
makes = ['Honda', 'Toyota', 'Audi']

for make in makes:
    filt = df['title'].str.contains(make, na=False)
    df.loc[filt, 'make']= make
    

#fig1
palette = sns.color_palette('rocket')
scatter=sns.scatterplot(data=df, x='price', y='mileage', hue='make', palette='muted')
scatter.set_title("Mileage vs Price")
scatter.set_xlabel("Price")
scatter.set_ylabel("Mileage")
plt.show()

#fig1 showing only Honda
filt = df['make']=='Honda'
filtered = df[filt]
scatter=sns.scatterplot(data=filtered, x='price', y='mileage', palette=palette)
scatter.set_title("Mileage vs Price")
scatter.set_xlabel("Price")
scatter.set_ylabel("Mileage")
plt.show()

#find outliers to identify few cars worth looking into further
def find_car(maxprice, maxmileage, make):
    x = df.loc[(df['make'] == make) & (df['mileage']<maxmileage) &(df['price']<maxprice)]
    return x
    
find_car(11000, 75000, 'Toyota')
find_car(14000, 80000, "Honda")


#fig 2
df_agg = df.groupby([df['year'], 'make'])['price'].mean().to_frame()
df_agg['mileage'] = df.groupby([df['year'], 'make'])['mileage'].mean()

fig, axes = plt.subplots(ncols=2, figsize=(10,5))
left = sns.lineplot(ax = axes[0], data=df_agg, x='year', y='price', hue='make')
left.set_xlabel("Year")
left.set_ylabel("Avg Price")
left.set_title("Effect of Year on Price")
right = sns.lineplot(ax = axes[1], data=df_agg, x='year', y='mileage', hue='make')
right.set_xlabel("Year")
right.set_ylabel("Avg Mileage")
right.set_title("Effect of Year on Mileage")
plt.subplots_adjust(wspace=0.3)
plt.show()

#we see that each passing year yields an increase in price, with little exception. I wanted to see whether there would be a range of say 3 years where avg price was constant so I could lean towards buying the newest of the 3, but it looks like this is not the case.
#(with exception to Audi with only data until 2017), 2012-2019 for all makes yield a similar avg mileage. This indicates I should have success finding cars with low mileage towards the beginning of that year range, at a discounted price.


#fig 3
#extract lowest 15 mileages
fil = df[df['make']=='Honda']
fil = fil.sort_values('mileage', ascending=True)
lowest_15_H = fil.head(15)
lowest_15_H.rename(columns = {'year' : 'Year', 'price' : 'Price', 'mileage':'Mileage'}, inplace = True) 

fil = df[df['make']=='Toyota']
fil = fil.sort_values('mileage', ascending=True)
lowest_15_T = fil.head(15)
lowest_15_T.rename(columns = {'year' : 'Year', 'price' : 'Price', 'mileage':'Mileage'}, inplace = True) 

#extract lowest 15 prices 
fil2 = df[df['make']=='Honda']
fil2 = fil2.sort_values('price', ascending=True)
lowest_15_HP = fil2.head(15)
lowest_15_HP.rename(columns = {'year' : 'Year', 'price' : 'Price', 'mileage':'Mileage'}, inplace = True) 

fil2_T = df[df['make']=='Toyota']
fil2_T = fil2_T.sort_values('price', ascending=True)
lowest_15_TP = fil2_T.head(15)
lowest_15_TP.rename(columns = {'year' : 'Year2', 'price' : 'Price', 'mileage':'Mileage'}, inplace = True) 
lowest_15_TP['Year'] = lowest_15_TP['Year2'].astype('int32')
lowest_15_TP.dtypes

#plot of fig 3
fig, axes = plt.subplots(nrows = 2, ncols = 2, figsize=(10,5))
scatter1=sns.scatterplot(ax=axes[0,0], data=lowest_15_H, x='Year', y='Mileage',color=palette[1])
scatter1.set_title("Lowest 15 Mileages for Honda")
scatter1.set_xticks(range(2010,2024,2))
scatter1.set_xlabel('')
scatter2=sns.scatterplot(ax=axes[1,0],data=lowest_15_T, x='Year', y='Mileage', color= palette[4])
scatter2.set_title("Lowest 15 Mileages for Toyota")
scatter2.set_xticks(range(2010,2024,2))
plt.subplots_adjust(hspace=0.5)

scatter1=sns.scatterplot(ax=axes[0,1], data=lowest_15_HP, x='Year', y='Price', color=palette[1])
scatter1.set_title("Lowest 15 Prices for Honda")
scatter1.set_xticks(range(2010,2024,2))
scatter1.set_xlabel('')
scatter2=sns.scatterplot(ax=axes[1,1],data=lowest_15_TP, x='Year', y='Price', color=palette[4])
scatter2.set_title("Lowest 15 Prices for Toyota")
scatter2.set_xticks(range(2010,2024,2))
plt.subplots_adjust(wspace=0.4)
plt.show()

#from this current range of data, we see some of the lowest 15 mileages for Honda are actually in the 2015-2018 range surprisingly, so maybe I can get a steal with some of those. Toyota is a bit more scattered but still some in that range. I was expecting the lowest 15 mileages to be all the newest cars.
#from this current range of data, we see the majority of the lowest priced vehicles are obviously the older ones in the dateframe. However, there are some potential steals: the 2015 Honda and 2014-2017 Toyotas shown are all worth looking into to see if there is an underlying factor driving these prices down.











