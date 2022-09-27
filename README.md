# Multiy-Currency Accounting

#### Video Demo:  <URL HERE>

#### Description:

##### 00. Why I develope this app

This is my final project for CS50 course. It's a web app based on Flask. I deployed it on Azure so you can visit it from the link [https://currency-acc.azurewebsites.net/](https://currency-acc.azurewebsites.net/).

I have my monthly credit bill in many different currencies, for example, I have my Playstation account in Hongkongs store which trade in HKD, and my Nintendo Switch account in Japanese store which trade in JPY, I currently living in Sweden, daily cost is in SEK but some online services(for example, Steam :)) are in EUR and USD. Also, if I travel to some other countries in Schengen area, there are more different currencies will be in my bill. And in the end, I need to pay the bill in CNY, because my credit card is issued by a Chinese bank.

So a tool that I want, is an accounting system. It can help me trace back my costs in different currencies. And by the end, caculate the sum of my cost.

You might say, does not your credit card bank have already done that for you? Yes, but I have another request: Compare the bill from the bank, which many fees are included, with the number which caculated without any fee included. In this way can I figure out which bank provide the "best" service.

##### 01. What it for:

This app will help you record the cost in different currencies(as many as you want!), and exchange the cost from the currency that it happend, to the destinate currency that you nominated, by the exchange rates of the day when trade was happened. 

##### 02. If you want to modified:

1. This app is based on Flask of Python. 
2. It uses Psycopg to manipulate PostgreSql database. A table to record information for all users, a table to record the exchange rates of each day that been searched for(reducing the usage of api), a table for a user to record the users accounting data.
3. Page style is based on Boostrap 5.
4. Exchange rates information is from [https://openexchangerates.org/](https://openexchangerates.org/).