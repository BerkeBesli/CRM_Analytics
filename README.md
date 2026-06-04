<div align="center">
  <img src="https://github.com/BerkeBesli/CRM_Analytics/blob/main/CRMimage.png?raw=true" alt="CRM Analytics Banner" width="800">
</div>

# CRM Analitiği (CRM Analytics)

Bu depo, Müşteri İlişkileri Yönetimi (CRM) süreçlerinin veri analitiği yöntemleriyle incelendiği ve modellendiği Python betiklerini içermektedir. Proje, veri setleri üzerinden müşteri segmentasyonu ve yaşam boyu değeri tahminleme gibi analitik CRM problemlerini ele almaktadır.

## 📂 Proje İçeriği ve Dosya Yapısı

Betikler, teorik kavramlardan başlayarak makine öğrenmesi ve olasılıksal istatistik modelleriyle tahminlemeye doğru ilerleyen bir yapıda kurgulanmıştır.

* **`1-IntroToCRM.py`**: CRM temel kavramları, müşteri yaşam döngüsü ve temel performans göstergeleri (KPI, Churn Rate, Retention Rate) üzerine teknik notlar.
* **`2-RFMnotes.py`**: RFM (Recency, Frequency, Monetary) metriklerinin çalışma mantığı ve skorlama algoritmaları.
* **`3-RFM-Segmentation.py`**: Online perakende veri seti kullanılarak müşterilerin RFM metriklerine göre hesaplanması, segmentlere (ör. *Loyal Customers*, *At Risk*) ayrılması ve sürecin fonksiyonlaştırılması.
* **`4-CLTV.py`**: Müşteri Yaşam Boyu Değeri (Customer Lifetime Value - CLTV) denkleminin kurulması, hesaplanması ve müşterilerin bu değere göre segmentasyonu.
* **`5-CLTVprediction.py`**: BG/NBD (satın alma frekansı tahmini) ve Gamma-Gamma (ortalama karlılık tahmini) modelleri ile zaman projeksiyonlu olasılıksal CLTV tahmini yapılması.

## ⚙️ Gereksinimler

Analiz ortamını hazırlamak ve betikleri çalıştırmak için aşağıdaki Python kütüphanelerinin kurulu olması gerekmektedir:

```bash
pip install pandas numpy scikit-learn lifetimes openpyxl
