# HCI_Project
Sentimental analysis using Linguistic approach

The flask application placed in the project can be directly executed without any requirement.
I initially used my own Prediction API but was not able to share it because of credentials and security issue.
Thus I used Mashape API which can be used by anyone,create an account and place the key in the flaskapp.py.

We used EC2 Instance to run our application but it can be executed independently.
Before running flaskapp.py make sure following prerequisites are satisfied.
1. Mongo DB is installed and running on the same server where you are plnning to runn flaskapp.py.
2. Make sure you have python 2.7 and packages like pymongo, unirest and bycrypt.
3. We used ubuntu 14.04 server along with apache using wsgi or else you can directly run flaskapp.py which will ultimately run the app on localhost at port 5000.

After running the application you can use it using 'loclhost:5000' as URL in Browser.

