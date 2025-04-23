# aml_project
Project for building pipeline and machine learning
this project simulates the real world project building starting from exporting data into cloud and developing microservice for each task.


# **Initial research**
The datasets are taken from Kaggle a SAML-D version of antimoney laundering which is a synthetic data curated by IBM.
**Research and Eda on data**  </br>
Data columns (total 12 columns):  </br>
    Column                  Dtype    </br>
---  ------                  -----    </br>
 0   Time                    object  </br>
 1   Date                    object   </br>
 2   Sender_account          int64    </br>
 3   Receiver_account        int64    </br>
 4   Amount                  float64  </br>
 5   Payment_currency        object   </br>
 6   Received_currency       object   </br>
 7   Sender_bank_location    object   </br>
 8   Receiver_bank_location  object   </br>
 9   Payment_type            object   </br>
 10  Is_laundering           int64    </br>
 11  Laundering_type         object   </br>
dtypes: float64(1), int64(3), object(8)  </br>
memory usage: 870.2+ MB  </br>

There was  9504852 records, 12 columns and of size 870MB.  </br>
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


# **model building and training**
two model were trained XGboost classifier and Random forest classifer.
the best accuracy was from random forest</br>
**Accuracy**: 0.8911 — This means that the model correctly classified 89.11% of all instances. While not perfect, it is relatively high.</br>

**Precision**: 0.9990 — This is a very strong score, meaning that when the model predicts a positive (fraudulent transaction), it is almost always correct. This is crucial in fraud detection, as false positives are costly. </br>

**Recall**: 0.8911 — This is also fairly high, indicating that the model is good at identifying fraudulent transactions. However, it is lower than precision, meaning there might be some false negatives (fraudulent transactions missed by the model).</br>

**F1-score**: 0.9414 — The F1-score is the harmonic mean of precision and recall, and it's high, which suggests that the model has a good balance between precision and recall. </br>

**ROC-AUC**: 0.9914 — The ROC-AUC score close to 1.0 indicates that the model has an excellent ability to discriminate between the positive and negative classes (fraud and non-fraud). </br>


# Architecure 

## Starting with backend
The source directory of a project is src.</br>
src/components  *for each pipeline stages main logic and task binding* </br>
src/config *the spark session* </br>
src/constant *the constant used in project*</br>
src/DB *for sql server connection*</br>
src/entity *for entity and input and artifact each component they generate* </br>
src/file_insertion *for inserting data into sql server*</br>
src/kafka_fetch *for messaging data*</br>`  
src/ml *for sql customize transformation and  logic for loading old model*</br>
src/pipeline *executing each pipeline in sequence* </br>
### running the code</br>
To run the code, start by creating conda environment and store data into your google cloud and enable apis and download json file.</br>
`conda create -p .conda python=3.11 -y` </br>
`run insert.py` to store data into sql server but don;t forget to change the credentials  </br>
</br>

![Chart](https://github.com/k17hawk/aml_project/blob/main/images/my-chart.jpeg)
### microservice for training model </br>
Use you own IP,sql server detils  and own mongoDB API </br>
 build the docker file Dockerfile </br>
`docker build -t mypyspark:latest .`
 save the docker file </br>
`docker save -o mypyspark.tar mypyspark:latest`
load into minique </br>
`minikube load mypyspark.tar` 
 add the addonis </br>
`minikube addons enable csi-hostpath-driver`
 creat argo namespace   </br>
`kubectl create namespace argo`
install argo-workflow </br>
`helm install argo-workflows argo/argo-workflows -n argo`  
edit workflow and patch with  </br>
`kubectl -n argo patch deployment argo-workflows-server  --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--auth-mode=server"}]'`
install my-chart microservice </br>
`helm install my-chart ./my-chart -n argo` 
view the UI  </br>
`kubectl port-forward svc/argo-workflows-server -n argo 2746:2746` 

![Chart](https://github.com/k17hawk/aml_project/blob/main/images/gcs-microservice.jpeg)
### microservice to fetch the data for prediction </br>
 build docker file </br>
`docker build -f Dockerfile.python -t pythonkafka:latest .`
`docker save -o pythonkafka.tar pythonkafka:latest` save it </br>
`minikube image load pythonkafka.tar` load it </br>
`enable bitnami by installing it` </br>
`helm install kafka -n argo bitnami/kafka --version 29.3.14 -f kafka-values.yaml` the kafka-values.yaml are in my-chart  </br>
`kubectl run -n argo kafka-client --restart='Never' --image docker.io/bitnami/kafka:3.7.1-debian-12-r4 --namespace default --command -- sleep infinity` kafka client for creating topics </br>
`kubectl exec --tty -i kafka-client --namespace default -- bash` </br>
`kafka-topics.sh --create --bootstrap-server kafka.argo.svc.cluster.local:9092 --topic my-gcs-data --partitions 3 --replication-factor 2` </br>
Now store data into aml-data-bucket/predictions in your google cloud</br>
also enable and give permission for pub/sub topic notification </br>
`kubectl create secret generic gcp-service-account --from-file=key.json=path/to/data-prediction-pipe-data-61d5e9bb16fa.json -n argo` </br>
`helm install gcs-microservice ./gcs-microservice -n argo` </br>

![Chart](https://github.com/k17hawk/aml_project/blob/main/images/prediction-chart.jpeg)
### microservice for prediction  </br>
`docker build -f Dockerfile.spark -t pythonspark:latest .` </br>
`docker save -o pythonspark.tar pythonspark:latets` </br>
`minikube image load pythonspark.tar` </br>
`helm install prediction-chart ./predicton-chart -n argo` </br>
