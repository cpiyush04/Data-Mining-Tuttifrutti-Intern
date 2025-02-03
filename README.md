# Data-Mining-Tuttifrutti-Intern
This repository contains scripts and resources for extracting data from Kickstarter

## Scraper
Selenium script to extract commentator names and their profile pictures from Kickstarter project pages. The scraper uses **Selenium** with **undetected-chromedriver** to bypass detection mechanisms and load the Kickstarter pages efficiently.

## Install Dependencies
```bash
pip install -r Requirements.txt
```
The requirements.txt file includes the following dependencies:
```
pandas==1.5.3
selenium==4.8.0
undetected-chromedriver==3.1.5
openpyxl==3.1.5
```
Make sure you have Google Chrome installed, as the scraper uses the Chrome WebDriver.

1. to extract the commentator names and their associated profile pictures from a Kickstarter project, run:
```bash
python Commentator_Detail_Scraper.py
```
2. To search for gamers' social media profiles on Google, execute:
```bash
python user_account_search_automation.py
```  
3. Additional script - to collect the number of comments available for a specific Kickstarter project, run
```bash
python Number_of_Comments.py
```
   
### Author

This code is developed and maintained by Piyush Chandra.  
You can contact me at piyushchandra004@gmail.com.
