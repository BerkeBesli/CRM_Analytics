# RFM = Recency, Frequency, Monetary -> Bu üçü RFM metrikleridir.
# RFM analizi, müşteri segmentasyonu için kullanılan bir tekniktir.
# Müşterilerin satın alma alışkanlıkları üzerinden gruplanması ve gruplara özel stratejiler geliştirilebilmesini sağlar.
# CRM çalışmaları için birçok başlık altında veriye dayalı aksiyon alma imkanı sağlar.

###############################################################################
# RFM Metrikleri;
# Recency -> Müşterinin yeniliğini/sıcaklığını veya bizden son alışveriş yaptığı durumunu temsil eder
# Recency metriği düşük tercih edilir. Örneğin gün olarak, 1 gün ve 70 gün arasında 1 gün önce işlem yapan

# Frequency -> Müşterinin işlem sayısını veya ne kadar sıklıkla alışveriş yaptıüı durumunu temsil eder
# Frequency'de en yüksek değer tercih edilir.

# Monetary -> Müşterinin getirdiği kazancı/parasal değeri temsil eder.
# Monetary için de en yüksek değer tercih edilir.

# Bu metrikler hem kendi içlerinde hem de birbirleri arasında kıyaslanabilir yapılmalıdır.
# Bu yüzden RFM metriklerini, RFM skorlarına dönüştürmek gereklidir.

############################################################################
# RFM Skorları
# RFM metrikleri, RFM skorlarına dönüştürüldüğünde aynı cinsden ifade edilebilir hale gelir.
# Örneğin RFM değerleri R:80  F:250  M:52OO olan bir müşteriyle
# RFM değerleri R:7  F:560  M:2300 olan bir müşterinin arasındaki değeri ayırt etmek için
# Değerler 1'le 5 arasında ifade edilir ve RFM skorları bulunur.

# Bu şekilde ilk müşterinin skoru R:1, F:4, M:5 -> 145
# İkinci müşterinin skoru R:4, F:5, M:4 -> 454
# Bunlardan ilk müşterinin R değerinin büyük olması, skorunun düşük olduğunu ama getirdiği değerin yüksek olduğunu,
# İkinci müşterinin ise dengeli ve iyi bir skoru olduğunu görebiliriz.

##########################################################################
# Skorlar Üzerinden Segmentasyon
# Skorlar aynı cinsden ifade etmeye yararlı olsa da birçok skor kombinasyonunu ayırt etmek hala kolay değildir.
# Bunlar ile mantıklı sınıflar oluşturarak, daha ayırt edilebilir şekilde mantıklı değerler versin.

# Bu sınıflar oluşturulurken R ve F değerine daha çok bakılır. R ve F değerleri getirilen paradan daha önemlidir
# Müşteri nadiren ve az sayıda alışveriş yaptığında, getirdiği para değeri tekrarlanabilir olmaz.
# Fakat müşteri sık ve çok sayıda alışveriş yaparsa getirdiği para değeri o kadar daha değerli olur
