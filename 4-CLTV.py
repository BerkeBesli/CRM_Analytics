# Customer Lifetime Value
# Müşterinin bir şirketle ilişkisi süresince bu şirkete kazandıracağı parasal değer
# CLTV = (Customer Value / Churn Rate) * Profit Margin
# Customer Value = Average Order Value * Purchase Frequency

# Average Order Value = Total Price / Total Transaction (Order)
# Purchase Frequency = Total Transaction / Total Number of Customers
# Churn Rate (Müşteri Terk Oranı) = 1 - Repeat Rate
# Repeat Rate = Customers That Order More Than Once / All Customers
# Profit Margin = Total Price * 0.10

# Müşterilerin CLTV değerlerinden segmentasyon yapılabilir

##################################################################
# 1. Veriyi Hazırlama

# Değişkenler;
# InvoiceNo: Fatura numarası, her işleme ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu, her ürün için eşsiz numara.
# Description: Ürün ismi.
# Quantity: Ürün adedi. Faturalardaki ürünlerde kaçar tane satıldığını ifade eder.
# InvoiceDate: Fature tarihi ve zamanı.
# UnitPrice: Ürün fiyatı.
# CustomerID: Eşsiz müşteri numarası.
# Country: Müşterinin yaşadığı ülke.

import datetime as dt
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option("display.float_format", lambda x: '%.5f' % x)
df_ = pd.read_excel('C:/Users/Sigma/PycharmProjects/CRM/online_retail_II.xlsx', sheet_name='Year 2009-2010')
df = df_.copy()
df.head()

df = df[~df["Invoice"].str.contains("C",na=False)]
df = df[(df["Quantity"]>0)]
df.isnull().sum()  # Kaç boş değer var görmek için
df.dropna(inplace=True)

df.describe().T
df["TotalPrice"] = df["Quantity"] * df["Price"]

cltv_c = df.groupby("Customer ID").agg({"Invoice": lambda x: x.nunique(),
                                        "Quantity": lambda x: x.sum(),
                                        "TotalPrice": lambda x: x.sum()})

cltv_c.columns = ["TotalUnit", "TotalTransaction", "TotalPrice"]

###########################################################################
# 2. Average Order Value (Total Price / Total Transaction)

cltv_c.head()
cltv_c["AvgOrderValue"] = cltv_c["TotalPrice"] / cltv_c["TotalTransaction"]

###########################################################################
# 3. Purchase Frequency (Total Transaction / Total Number of Customers)

cltv_c["PurchaseFrequency"] = cltv_c["TotalTransaction"] / cltv_c.shape[0]

###########################################################################
# 4. Repeat Rate & Churn Rate (Birden fazla alışveriş yapan müşteri sayısı / tüm müşteriler)

cltv_c[cltv_c["TotalTransaction"] > 1].index.nunique() / cltv_c.index.nunique()
# ya da
repeatrate = cltv_c[cltv_c["TotalTransaction"] > 1].shape[0] / cltv_c.shape[0]
# Shape ile boyutları görüntülenir ve ilk indexte kaç row olduğu yazdığı için müşteri sayısını verir

churnrate = 1 - repeatrate

##########################################################################
# 5. Profit Margin (Total Price * 0.10)  -> 0.10 sabit sayı olarak verildi, şirket bu değeri verir

cltv_c["ProfitMargin"] = cltv_c["TotalPrice"] * 0.10

##########################################################################
# 6. Customer Value (Average Order Value * Purchase Frequency)

cltv_c["CustomerValue"] = cltv_c["AvgOrderValue"] * cltv_c["PurchaseFrequency"]

########################################################################
# 7. Customer Lifetime Value ((Customer Value / Churn Rate) * Profit Margin)

cltv_c["CLTV"] = (cltv_c["CustomerValue"] / churnrate) * cltv_c["ProfitMargin"]
cltv_c.sort_values(by="CLTV", ascending=False).head()
cltv_c.describe().T

########################################################################
# 8. Segmentlerin Oluşturulması

cltv_c["Segment"] = pd.qcut(cltv_c["CLTV"], 4, labels=["D", "C", "B", "A"])
# Qcut küçükten büyüğe istenen değişkeni sıralar ve q ile belirtilen sayıya böler
# 4 dendiğinde %0-%25, %25-50, %50-75... şeklinde böler ve en küçük kısıma D en büyüğe A etiketi verilir

cltv_c.head()
cltv_c.groupby("Segment").agg({"count", "mean", "sum"})

cltv_c.to_csv("CLTV.csv")

#########################################################################
# Tüm Süreçlerin Fonksiyonlaştırılması

def create_cltv_c(dataframe, profit=0.10):
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[(dataframe["Quantity"] > 0)]
    dataframe.dropna(inplace=True)
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    cltv_c = dataframe.groupby("Customer ID").agg({"Invoice": lambda x: x.nunique(),
                                                   "Quantity": lambda x: x.sum(),
                                                   "TotalPrice": lambda x: x.sum()})

    cltv_c.columns = ["TotalTransaction", "TotalUnit", "TotalPrice"]

    cltv_c["AvgOrderValue"] = cltv_c["TotalPrice"] / cltv_c["TotalTransaction"]
    cltv_c["PurchaseFrequency"] = cltv_c["TotalTransaction"] / cltv_c.shape[0]
    repeatrate = cltv_c[cltv_c.TotalTransaction > 1].shape[0] / cltv_c.shape[0]
    churnrate = 1 - repeatrate
    cltv_c["ProfitMargin"] = cltv_c["TotalPrice"] * profit
    cltv_c["CustomerValue"] = cltv_c["AvgOrderValue"] * cltv_c["PurchaseFrequency"]
    cltv_c["CLTV"] = (cltv_c["CustomerValue"] / churnrate) * cltv_c["ProfitMargin"]
    cltv_c["Segment"] = pd.qcut(cltv_c["CLTV"], 4, labels=["D", "C", "B", "A"])
    return cltv_c

df = df_.copy()
create_cltv_c(df)

