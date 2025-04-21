# aml_project
Project for building pipeline and machine learning
this project simulates the real world project building starting from exporting data into cloud and developing microservice for each task.


# **Initial research**
The datasets are taken from Kaggle a SAML-D version of antimoney laundering which is a synthetic data curated by IBM.
**Research and Eda on data**

Data columns (total 12 columns):
 #   Column                  Dtype  
---  ------                  -----  
 0   Time                    object 
 1   Date                    object 
 2   Sender_account          int64  
 3   Receiver_account        int64  
 4   Amount                  float64
 5   Payment_currency        object 
 6   Received_currency       object 
 7   Sender_bank_location    object 
 8   Receiver_bank_location  object 
 9   Payment_type            object 
 10  Is_laundering           int64  
 11  Laundering_type         object 
dtypes: float64(1), int64(3), object(8)
memory usage: 870.2+ MB

There was  9504852 records, 12 columns and of size 870MB.
The bulk of the transactions were below 10K, with the median being 6,113.72, and 75% of transactions were below 10.5K.</br>
At the 90th percentile, it as  already at 16,560.85, indicating that the higher value transactions were becoming less frequent, but they still represent a significant portion of the data.</br>
The 99th percentile (45K) shows that only 1% of the transactions were larger than 45K. This means the majority of the data is heavily concentrated in smaller amounts.</br>

Large transactions in the 99th percentile could be flagged for review, but intermediate values between the 75th and 90th percentiles has a gradual increases (a sign of layering??).

There were many transactions around the 10K mark, it could also indicate smurfing.
Analysis for smurfing(structuring behaviours)
The bimodal distribution where data transactions tend to cluster around two separate ranges of amounts.
**First Peak (Low Amounts)**: The first peak is very prominent and occurs at the lower end of the amount range (around 0 to 1000). This indicates a high concentration of transactions with relatively small values.</br>
**Second Peak (Higher Amounts)**: The second peak is broader and occurs in the higher amount range (roughly 4500 to 10000). This suggests a significant number of transactions also fall within this higher range. </br>
**Dip in the Middle**: There's a noticeable dip or valley between the two peaks (around 3000 to 4500). This indicates a lower frequency of transactions within this middle range.</br>
**Right Skewness**: Overall, the distribution exhibits a right skew. This suggests the presence of some larger transactions, even though the majority are concentrated in the two peaks.
**Unusual Pattern**: The distinct dip in the middle of the distribution is somewhat unusual. It could indicate a specific characteristic of the system or a deliberate attempt to avoid transactions in that range.
**Investigate the Context**
Temporal Patterns using Date and time
The specific times of day or days of the week when these transactions were more frequent.
The busiest time of a  day is 1PM with the transaction 396676 but still The transaction counts are consistently very high across these peak hours.Also there was no transaction  for the month of Sepetember within  2 years
**Potential Money Laundering Patterns** </br>
*Overlap with Business Hours*:</br>

Both laundering and non-laundering transactions peak during business hours (8 AM - 5 PM). </br>
*Laundering activity slightly favors* morning hours (8-11 AM), which could indicate attempts to blend with legitimate business transactions.</br>
**Drop in Illicit Transactions in Early Morning**:</br>
Night-Time Transactions (10 PM - 12 AM) Show Higher Laundering Ratios

***Peak Months for Suspected Money Laundering Transactions**:</br>

The highest volume of transactions (laundering) occurs in May (669,317 transactions), followed by January (663,098) and March (662,393).
The lowest recorded activity is in August (478,700 transactions) and October (519,961 transactions).
Since  May is the busiest month for regular transactions, and increasing in laundering cases (629).
</br>

**Peak Months for Non-Laundering Transactions**: </br>
The highest  non money laundering activity occurs in June (793 transactions), followed by July (754) and April (713).
</br>
**Seasonal Trends & Possible Explanations** </br>

During December holidays and summer vacations (may-June-July), legitimate businesses see a rise in transactions, making it easier for criminals to blend illegal money into the system without triggering alarms. </br>
**Year-End Drop** High laundering cases in January and May, both critical periods for financial audits and tax filings</br>
**Mismatch with Normal Transactions**: Money laundering transactions peak in may, while legitimate transactions peak in June.

The UK is known for having massive banking transactions due to its status as a global financial hub, attracting significant investment and financial activity from around the world.