# RFM ile Müşteri Segmentasyonu

# 1. İş Problemi
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


####################################################
# 2. Veriyi Anlama

import datetime as dt
import numpy as np
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option("display.float_format", lambda x: '%.5f' % x)

df_ = pd.read_excel('C:/Users/Sigma/PycharmProjects/CRM/online_retail_II.xlsx')
df = df_.copy()
df.head()
df.shape
df.isnull().sum()

# Eşsiz ürün sayısı nedir ?
df["Description"].nunique()

# Hangi üründen kaç tane satıldı ?
df["Description"].value_counts().head()

df.groupby("Description").agg({"Quantity": "sum"}).head(10)
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head(10)

# Kaç farklı fatura vardır ?
df["Invoice"].nunique()

# Ürün satın alımların toplam fiyatları
df["TotalPrice"] = df["Quantity"] * df["Price"]

# Fatura başına toplam harcanan miktar
df.groupby("Invoice").agg({"TotalPrice": "sum"}).head(10)


###########################################################
# 3. Veri Hazırlama

df.isnull().sum()  # Eksik değer sayısını görmek için
df.dropna(inplace=True)  # Eksik değerleri silmek için

# Invoice'de başında C olanlar iade olan ürünleri temsil ediyor
# İade olan faturaları verisetinden çıkartarak, (-) değerler çıkartılabilir.

df = df[~df["Invoice"].str.contains("C", na=False)]

# Bu şekilde C olanların dışındakiler seçilerek, veriseti (-) değerlerden arındırılır.


###########################################################
# 4. RFM Metriklerinin Hesaplanması (Recency, Frequency, Monetary)

df["InvoiceDate"].max()
today_date = dt.datetime(2010,12,11) # Datetime kütüohanesi ile datetime tipinde oluşturulan tarih

# Alt satırdaki işlem ile kullanıcıların özgün Customer ID'lerine göre satın alımlar gruplanır
# sonra sözlük yapısıyla değişkenler ve değişkenlere uygulanacak fonksiyonlar yazılır.
# Groupby ile tüm müşteriler tekilleşir ve tek tek bilgileri incelenebilir.
# Lambda ile yazılan kullan at fonksiyonlar değişkenlerin hepsine tek tek uygulanır.

rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     "Invoice": lambda Invoice: Invoice.nunique(),
                                     "TotalPrice": lambda TotalPrice: TotalPrice.sum()})

# Bu değişiklikler ile InvoiceDate, Recency'i temsil eder, Invoice, Frequency'i temsil eder ve TotalPrice = Monetary
rfm.head()
rfm.columns = ["Recency", "Frequency", "Monetary"]
rfm.describe().T  # Buraya bakıldığında bazı monetary değerlerinin 0 olduğu görülür ve bu bir yanlışlık olduğu belirtisidir

rfm = rfm[rfm["Monetary"] > 0] # Bu şekilde 0 değerleri silinir
rfm.shape # Shape ile yeni veri setinde 4314 müşterinin olduğunu ve 3 metriğe ayırdığımız görülür.


############################################################
# 5. RFM Skorlarının Hesaplanması

rfm["recency_score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1])
# Qcut ile değişken küçükten büyüğe sıralanır ve 5 parçaya bölünerek, parçalara labeldaki isimlendirmeler verilir.
# Örneğin 0-100 arası değerler varsa, 0-20, 20-40, 40-60, 60-80, 80-100 şeklinde 5 parçaya ayrılırdı
# ve sonra recency için 0-20 gün arasındakiler 5, 20-40 gün arasındakiler 4 gibi skorlar alırdı
# Recency için gün sayısının az olması, yüksek skor anlamına gelir.
# Bu yüzden qcut küçükten büyüğe sıraladığı için, labellar büyükten küçüğe sıralanır ve az gün, yüksek skor alır.

rfm.head()
rfm.describe().T

rfm["monetary_score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5])
# Monetary score için ne kadar büyük para değeri varsa o kadar yüksek skor alır
# qcut küçükten büyüğe sıraladığı için labellar da küçükten büyüğe verilir

# rfm["frequency_score"] = pd.qcut(rfm["Frequency"], 5, labels=[1, 2, 3, 4, 5])
# Yukarıdaki gibi frequency skorları tanımlanmaya çalıştığında, sürekli tekrarlayan değerlerden hata döner.
# Farklı aralıklara aynı değerler atanması sorun yaratacağından bunu çözmek için;

rfm["frequency_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
# Rank(method=first) ile ilk gördüğüne atama komutu vererek bu problem çözülür

rfm["RFM_score"] = (rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str))
# Müşteri segmentasyonunu R ve F değerleri ile yapabildiğim için Monetary'i katmaya gerek yok.

rfm[rfm["RFM_score"] == "55"] # Bu tanım ile şampiyon sınıfındaki müşteriler görülebilir
rfm[rfm["RFM_score"] == "11"] # Önemsiz müşteriler


##########################################################
# 6. RFM Segmentlerinin Oluşturulması ve Analizi

seg_map = {
    r"[1-2][1-2]": "hibernating",
    r"[1-2][3-4]": "at_risk",
    r"[1-2]5": "cant_lose",
    r"3[1-2]": "about_to_sleep",
    r"33": "need_attention",
    r"[3-4][4-5]": "loyal_customers",
    r"41": "promising",
    r"51": "new_customers",
    r"[4-5][2-3]": "potential_loyalists",
    r"5[4-5]": "champions"
}

rfm["Segment"] = rfm["RFM_score"].replace(seg_map, regex=True)

rfm[["Segment", "Recency", "Frequency", "Monetary"]].groupby("Segment").agg(["mean", "count"])

rfm[rfm["Segment"] == "need_attention"].head() # Segmentasyon sonrası istenen grupların bilgilerine rahatça bakılır.
rfm[rfm["Segment"] == "need_attention"].index  # İstenen gruptaki müşterilerin Customer Id'lerine bakılabilir.

new_df = pd.DataFrame()
new_df["Şampiyonların ID'leri"] = rfm[rfm["Segment"] == "champions"].index
new_df["Şampiyonların ID'leri"] = new_df["Şampiyonların ID'leri"].astype(int) # Ondalık sayılardan kurtulmak için
new_df.to_csv("Şampiyonlar.csv")

rfm.to_csv("RFM.csv")
# Bu şekilde segmentler veya müşteriler hakkında bilgiler isteğe göre ayrılabilir ve verisetine dönüştürülür.
# Sonrasında ilgili departmana istenen bilgiler rahatça iletilebilir.
# Ya da istenen veriler kullanılarak başka işlemler yapılabilir.


############################################################################
# 7. Tüm Sürecin Script'e Çevrilmesi / Fonksiyonlaştırılması

def create_rfm(dataframe, csv=False):

    # Veriyi Hazırlama
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]

    # RFM Metriklerinin Hesaplanması
    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby("Customer ID").agg({"InvoiceDate": lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                                "Invoice": lambda Invoice: Invoice.nunique(),
                                                "TotalPrice": lambda TotalPrice: TotalPrice.sum()})

    rfm.columns = ["Recency", "Frequency", "Monetary"]
    rfm = rfm[rfm["Monetary"] > 0]

    # RFM Skorlarının Hesaplanması
    rfm["recency_score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1])
    rfm["monetary_score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5])
    rfm["frequency_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

    # CLTV (Customer Lifetime Value) skorları kategorik değişkene dönüştürülüp df'e eklendi
    rfm["RFM_score"] = (rfm["recency_score"].astype(str) +
                        rfm["frequency_score"].astype(str))

    # Segmentlerin İsimlendirilmesi
    seg_map = {
        r"[1-2][1-2]": "hibernating",
        r"[1-2][3-4]": "at_risk",
        r"[1-2]5": "cant_lose",
        r"3[1-2]": "about_to_sleep",
        r"33": "need_attention",
        r"[3-4][4-5]": "loyal_customers",
        r"41": "promising",
        r"51": "new_customers",
        r"[4-5][2-3]": "potential_loyalists",
        r"5[4-5]": "champions"
    }

    rfm["Segment"] = rfm["RFM_score"].replace(seg_map, regex=True)
    rfm = rfm[["Recency", "Frequency", "Monetary", "Segment"]]
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv("rfm.csv")

    return rfm


df = df_.copy()
rfm_new = create_rfm(df, csv=True)
rfm_new.head()
