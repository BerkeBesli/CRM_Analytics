# CLTV Prediction -> Zaman projeksiyonlu olasılıksal lifetime value tahmini
# Hatırlatma:
# Customer Value = Purchase Frequency (Number of Purchases) * Average Purchase Value
# Average Order Value = Total Price / Total Transaction (Order)
# Purchase Frequency = Total Transaction / Total Number of Customers
# Churn Rate (Müşteri Terk Oranı) = 1 - Repeat Rate
# Repeat Rate = Customers That Order More Than Once / All Customers
# Profit Margin = Total Price * 0.10

# CLTV = (Customer Value / Churn Rate) * Profit Margin

# Prediction yaparken kullanılan formül;
# CLTV = Expected Number of Transaction * Expected Average Profit
# Temelde aynı formülün farklı kelimelendirilmiş ve tahmine dayalı hali
# (Transaction = Purchase, Purchase Value = Profit)

# Bunun için iki farklı modelleme tekniği kullanılır
# CLTV = BG/NBD Model * Gamma Gamma Submodel

##################################################################################
# BG/NBD ile Expected Number of Transaction
# BG/NBD = Beta Geometric / Negative Binomial Distribution -> Satış tahmin modeli olarak kullanılır.
# Nam-ı Diğer -> Buy Till You Die modeli

# Bu model iki süreci olasılıksal olarak modeller;
# 1 - Transaction Process (Buy) -> İşlem / Satın Alma Süreci;
# Aktif olduğu sürece, belirli bir zaman periyodunda, bir müşteri tarafından gerçekleştirilecek,
# işlem sayısı transaction rate parametresi ile poisson dağılır.
# Transaction rate'ler her bir müşteriye göre değişir ve gamma dağılır.

# 2 - Dropout Process (Till You Die) -> İnaktif Olma / Bırakma / Markayı Terk Etme Süreci
# Her bir müşterinin dropout possibility'si (rate) vardır. Yani markadan uzaklaşma veya satın almayı bırakma ihtimali.
# Dropout rate'ler her bir müşteriye göre değişir ve tüm kitle için beta dağılır.

##################################################################################
# Gamma Gamma Submodel ile Exoected Average Profit
# Bir müşterinin işlemlerinin parasal değeri (monetary) transaction valueların ortalamasın etrafında rastgele dağılır.
# Ortalama transaction value, zaman içinde kullanıcılar arasında değişebilir fakat tek bir kullanıcı için değişmez.
# Ortalama transaction value, tüm müşteriler arasında gamma dağılır.

##################################################################################################

# BG/NBD ve Gamma Gamma ile CLTV Prediction

# 1 - Veriyi Anlamak
# Bir e-ticaret şirketi müşterilerini segmente ayırıp segmentlere göre stratejiler geliştirmek istiyor.
# Online retail veri seti İngiltere merkezli online bir satış mağazasının, 01/12/2009 - 09/12/2011 arasındaki satışları

# Değişkenler;
# InvoiceNo: Fatura numarası, her işleme ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu, her ürün için eşsiz numara.
# Description: Ürün ismi.
# Quantity: Ürün adedi. Faturalardaki ürünlerde kaçar tane satıldığını ifade eder.
# InvoiceDate: Fature tarihi ve zamanı.
# UnitPrice: Ürün fiyatı.
# CustomerID: Eşsiz müşteri numarası.
# Country: Müşterinin yaşadığı ülke.

# 2 - Veriyi Hazırlamak

# pip install lifetimes
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions
from sklearn.preprocessing import MinMaxScaler
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option("display.float_format", lambda x: '%.4f' % x)

# Modeller olasılıksal olacağından bu modelleri kurarken kullanılacak değişkenlerin dağılımı sonuçları etkiler.
# Bundan dolayı değişkenler oluşturulduktan sonra aykırı değerler tespit edilmeli ve baskılanmalıdır.
# Bunun için eşik değerleri değiştirilmelidir.
# Aykırı değerler, bir değişkenin genel dağılımının oldukça dışında olan değerlerdir.
# Yapılacak genellemelerin önüne geçen mantığı kaydıran değerlerdir.
# Bu tip değerler silmek istenmez, baskılanmak istenir.
# IQR = Interquantile Range = Çeyrekler Açığı

def outlier_thresholds(dataframe, variable):  # Kendisine girilen değişkenler için eşik değer belirlemeye kullanılır
    quantile1 = dataframe[variable].quantile(0.01)     # Çeyrek değerler hesaplanır
    quantile2 = dataframe[variable].quantile(0.99)
    interquantile_range = quantile2 - quantile1        # Çeyrek değerlerin farkı hesaplanır
    up_limit = quantile2 + 1.5 * interquantile_range   # 1. çeyreğin 1.5 IQR üstü
    low_limit = quantile1 - 1.5 * interquantile_range  # 2. çeyreğin 1.5 IQR altı
    return low_limit, up_limit

# Quantile ile çeyrekler hesaplanır, değişken küçükten büyüğe sıralanır.
# Normalde %25 ve %75lik değerlerden çeyrek hesabı yapılır
# Bu verisetine özel, çok az sayıda değerden kurtulmak istendiği için %1 ve %99 eşik olarak seçilir
# Çeyrekler arasındaki farkın 1.5 ile çarpılmış değeri, alt limit ve üst limiti oluşturmaya yarar.

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    # dataframe.loc[dataframe[variable] < low_limit, variable] = low_limit -> Eksi değer olmadığı için gereksiz
    dataframe.loc[dataframe[variable] > up_limit, variable] = up_limit

# Alt limit ve üst limitleri aşan değerleri, alt ve üst limit değeriyle değiştirme fonksiyonu

###############################################################################
# Verinin Okunması ve Ön İşleme

df_ = pd.read_excel('C:/Users/Sigma/PycharmProjects/CRM/online_retail_II.xlsx', sheet_name="Year 2010-2011")
df = df_.copy()
df.describe().T
df.head()
df.isnull().sum()
df.dropna(inplace=True)
df = df[~df["Invoice"].str.contains("C", na=False)]
df = df[df["Quantity"] > 0]
df = df[df["Price"] > 0]

replace_with_thresholds(df, "Quantity")
replace_with_thresholds(df, "Price")
df["TotalPrice"] = df["Quantity"] * df["Price"] # Bir ürüne ödenen toplam değer
today_date = dt.datetime(2011, 12, 11)

##################################################################################
# Lifetime Veri Yapısının Hazırlanması
# Recency : Son satın alma üzerinden geçen zaman. Haftalık. (kullanıcı özelinde)
# Frequency : Müşterinin satın alma sıklığı (tekrar eden toplam satın alma sayısı)
# Monetary : Satın alma başına ortalama kazanç -> (normalde toplam kazanca bakılır ama isteğe göre farklı kullanılır)
# T : Müşterinin yaşı. Haftalık. (Analiz tarihinden ne kadar önce ilk satın alma yapılmış)

cltv_df = df.groupby("Customer ID").agg({"InvoiceDate": [lambda InvoiceDate: (InvoiceDate.max() - InvoiceDate.min()).days,
                                                        lambda InvoiceDate: (today_date - InvoiceDate.min()).days],
                                         "Invoice": lambda Invoice: Invoice.nunique(),
                                         "TotalPrice": lambda TotalPrice: TotalPrice.sum()})

cltv_df.columns = cltv_df.columns.droplevel(0) # Değişken isimleri 2 taneden 1'e düşürüldü
cltv_df.columns = ["Recency", "T", "Frequency", "Monetary"] # Yeni isimler konuldu
cltv_df.head()

cltv_df["Monetary"] = cltv_df["Monetary"] / cltv_df["Frequency"] # Monetary değeri ortalama kazanca çevrildi
cltv_df.describe().T
cltv_df = cltv_df[cltv_df["Frequency"] > 1] # df 1den fazla alışveriş yapanlara indirgendi
cltv_df["Recency"] = cltv_df["Recency"] / 7 # Recency değeri haftalık değerler haline çevrildi
cltv_df["T"] = cltv_df["T"] / 7 # T değeri haftalık değerler haline çevrildi

#################################################################################
# BG/NBD Modelinin Kurulması

# Fit metodu kullanarak frequency, recency, T değerleri verildiğinde model oluşturur
# Beta ve Gamma dağılımları kullanılır, bu modelde parametreleri bulurken en çok olabilirlik yöntemi kullanılır
# Parametre bulmak için argüman gereklidir

bgf = BetaGeoFitter(penalizer_coef=0.001)

bgf.fit(cltv_df["Frequency"],  # Buradan a: 0.12, alpha: 11.41, b: 2.49, r: 2.18 değerleri bulundu.
        cltv_df["Recency"],
        cltv_df["T"],)

# 1 hafta içinde en çok satın alma beklediğimiz 10 müşteri kimdir ?

bgf.conditional_expected_number_of_purchases_up_to_time(1,
                                                        cltv_df["Frequency"],
                                                        cltv_df["Recency"],
                                                        cltv_df["T"]).sort_values(ascending=False).head(10)

bgf.predict(1,
            cltv_df["Frequency"],
            cltv_df["Recency"],
            cltv_df["T"]).sort_values(ascending=False).head(10)

cltv_df["ExpectedPurchaseWeek1"] = bgf.predict(1,
                                    cltv_df["Frequency"],
                                    cltv_df["Recency"],
                                    cltv_df["T"]).sort_values(ascending=False).head(10)

# Aylık bakmak istenirse;

cltv_df["ExpectedPurchaseMonthly"] = bgf.predict(4,    # Buradaki 4 hafta sayısını temsil eder
                                    cltv_df["Frequency"],
                                    cltv_df["Recency"],
                                    cltv_df["T"]).sort_values(ascending=False).head(10)

# Aylık şirketin beklediği toplam satış sayısı;

bgf.predict(4,
            cltv_df["Frequency"],
            cltv_df["Recency"],
            cltv_df["T"]).sum()

# Tahmin sonuçlarının değerlendirilmesi;

plot_period_transactions(bgf)
plt.show()

################################################################################################
# Gamma Gamma Modelinin Kurulması

ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(cltv_df["Frequency"], cltv_df["Monetary"]) # p: 3.79, q: 0.34, v: 3.73 bulunan sonuçlar

# İşlem sayısını ve ortalama kazancı argüman olarak vererek tahmini ortalama kazanç hesaplama fonksiyonu

ggf.conditional_expected_average_profit(cltv_df["Frequency"],
                                        cltv_df["Monetary"]).head(10)

# En yüksekden düşüğe doğru görmek için;
ggf.conditional_expected_average_profit(cltv_df["Frequency"],
                                        cltv_df["Monetary"]).sort_values(ascending=False).head(10)

cltv_df["ExpectedAverageProfit"] = ggf.conditional_expected_average_profit(cltv_df["Frequency"],
                                        cltv_df["Monetary"])

cltv_df.sort_values(by=["ExpectedAverageProfit"], ascending=False).head(10)

###################################################################################################
# BG-NBD ve GG modeli ile CLTV'nin hesaplanması

cltv = ggf.customer_lifetime_value(bgf,
                                   cltv_df["Frequency"],
                                   cltv_df["Recency"],
                                   cltv_df["T"],
                                   cltv_df["Monetary"],
                                   time=3,      # 3 aylık
                                   freq="W",     # T'nin frekans bilgisi
                                   discount_rate=0.01)

cltv.head()
cltv = cltv.reset_index()

cltv_final = cltv_df.merge(cltv, on="Customer ID", how="left")
cltv_final.sort_values(by="clv", ascending=False).head(10)

# Analiz yaparken veri setindeki başka değerleri incelemek, kıyaslamak ve aralarında patternler bulmak önemlidir.
# Analiz yapmak için başka değerlerle kıyaslama yapmakta yararlı, 3 aylık tahmini satış;

cltv_final["ExpectedPurchase3Months"] = bgf.predict(4 * 3,
                                        cltv_final["Frequency"],
                                        cltv_final["Recency"],
                                        cltv_final["T"]).sum()

# BG/NBD üzerinden CLTV hesaplaması yaparken kritik bir nokta;
# Normal şartlarda recency'nin düşük olması iyi değerlendirilirken, Buy Till You Die modelinde durum farklıdır.
# Bu modele göre düzenli bir müşteri eğer churn olmadıysa / dropout olmadıysa, yani müşteri markayı bırakmadıysa,
# kullanıcının recency değeri arttık.a alışveriş yapma ihtimali de yükseliyordur.

# CLTV final verisetinde recency ve frekansı düşük ama monetary yüksek değerli birimler yakalanmıştır.
# Monetary düşük ama recency ve frekansı yükske değerli birimler yakalanmıştır.
# Kısaca sadece tek özelliğe değil, özellikler bütününe bakarak müşterilerin deüerleri ölçülebilir hale gelmiştir.

##########################################################################################################
# CLTV'ye Göre Segmentlerin Oluşturulması

cltv_final["segment"] = pd.qcut(cltv_final["clv"], 4, labels=["D", "C", "B", "A"])
# qcut küçükten büyüğe sıralar ve %100 4 küçükten büyüğe 4 eşit aralığa böler

cltv_final.sort_values(by="clv", ascending=False).head(10)

cltv_final.groupby("segment").agg({"count", "mean", "sum"})

################################################################################################
# Çalışmanın Fonksiyonlaştırılması

def create_cltv_p(dataframe, month=3):
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[dataframe["Quantity"] > 0]
    dataframe = dataframe[dataframe["Price"] > 0]
    replace_with_thresholds(dataframe, "Quantity")
    replace_with_thresholds(dataframe, "Price")
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    todays_date = dt.datetime(2011, 12, 11)

    cltv_df = dataframe.groupby("Customer ID").agg(
        {"InvoiceDate": [lambda InvoiceDate: (InvoiceDate.max() - InvoiceDate.min()).days,
                         lambda InvoiceDate: (today_date - InvoiceDate.min()).days],
         "Invoice": lambda Invoice: Invoice.nunique(),
         "TotalPrice": lambda TotalPrice: TotalPrice.sum()})

    cltv_df.columns = cltv_df.columns.droplevel(0)
    cltv_df.columns = ["Recency", "T", "Frequency", "Monetary"]
    cltv_df["Monetary"] = cltv_df["Monetary"] / cltv_df["Frequency"]
    cltv_df = cltv_df[cltv_df["Frequency"] > 1]
    cltv_df["Recency"] = cltv_df["Recency"] / 7
    cltv_df["T"] = cltv_df["T"] / 7

    bgf = BetaGeoFitter(penalizer_coef=0.001)
    bgf.fit(cltv_df["Frequency"],
            cltv_df["Recency"],
            cltv_df["T"])

    cltv_df["ExpectedPurchaseWeek1"] = bgf.predict(1,
                                                   cltv_df["Frequency"],
                                                   cltv_df["Recency"],
                                                   cltv_df["T"])

    cltv_df["ExpectedPurchaseMonthly"] = bgf.predict(4,  # Buradaki 4 hafta sayısını temsil eder
                                                     cltv_df["Frequency"],
                                                     cltv_df["Recency"],
                                                     cltv_df["T"])

    cltv_df["ExpectedPurchase3Month"] = bgf.predict(13,  # Buradaki 4 hafta sayısını temsil eder
                                                     cltv_df["Frequency"],
                                                     cltv_df["Recency"],
                                                     cltv_df["T"])

    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(cltv_df["Frequency"], cltv_df["Monetary"])
    cltv_df["ExpectedAverageProfit"] = ggf.conditional_expected_average_profit(cltv_df["Frequency"],
                                                                               cltv_df["Monetary"])
    cltv = ggf.customer_lifetime_value(bgf,
                                       cltv_df["Frequency"],
                                       cltv_df["Recency"],
                                       cltv_df["T"],
                                       cltv_df["Monetary"],
                                       time=month,  # 3 aylık
                                       freq="W",  # T'nin frekans bilgisi
                                       discount_rate=0.01)
    cltv = cltv.reset_index()
    cltv_final = cltv_df.merge(cltv, on="Customer ID", how="left")
    cltv_final["segment"] = pd.qcut(cltv_final["clv"], 4, labels=["D", "C", "B", "A"])

    return cltv_final
df = df_.copy()
finalcltv = create_cltv_p(df)
finalcltv.to_csv("cltvprediction.csv")