# Used-Car-Search

The purpose of this code is to scrape vehicle information from Autotrader.com into a Pandas dataframe for easy analysis. It first takes a base url, with desired filters from the site, and loops through each page to get the first 500 records that meet set filters. For each page, using the Beautiful Soup library, it scrapes, the title, price, mileage, make, and year. The data is cleaned into a user-friendly dataframe that, from this point, can be used for any purpose.

I continued and performed exploratory analysis for my own personal car search, creating a function that takes in input of a max price, max mileage, and make, to help narrow down specific vehicles of interest from figure 1. 

Figure 1 plots all the observations by price and mileage.
Figure 2 shows the effect of year on price and mileage.
Figure 3 shows the lowest 15 mileages and prices, respectively, for both Honda and Toyota. 

Figures are produced from data from May 2023, but can be tweaked and duplicated for different datasets.
