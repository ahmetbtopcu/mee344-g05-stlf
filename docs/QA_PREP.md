# Q&A Hazırlığı ve Sözlü Sunum — G05

## Sunum dağılımı (10–15 dk)

| Üye | Slayt | Süre |
|-----|-------|------|
| Berhan Kaya | 1–3 | ~2 dk |
| Ahmet Bayram Topçu | 4–6 | ~3 dk |
| Yusuf Duman | 7–8 | ~2 dk |
| Furkan Efe Demirbel | 9–11 | ~3 dk |
| Tekgül Eroğlu | 12–15 + Q&A | ~3 dk |

## Anticipated Q&A

**S: Neden Decision Tree + AdaBoost?**  
C: Grup allocation (G05) gereği. DT yorumlanabilir baseline; AdaBoost aynı ailede boosting ile residual düzeltir.

**S: Neden üretim Toplam'ı target değil?**  
C: Toplam, kaynak sütunlarının toplamı — leakage. Target tüketim; üretim exogenous feature.

**S: Neden TimeSeriesSplit, KFold değil?**  
C: Zaman serisinde gelecek bilgisi train'e sızmasını önler.

**S: AdaBoost vs Gradient Boosting?**  
C: AdaBoost örnek ağırlıklarını günceller; GB gradient descent ile residual. İkisi de boosting ailesi.

**S: Overfitting var mı?**  
C: CV RMSE (1079) vs test RMSE (1040) yakın — ciddi overfit yok. max_depth grid ile sınırlandı.

**S: En önemli feature'lar?**  
C: lag_24h, lag_168h, cyclic hour, roll_mean_24h. Permutation importance ile doğrulandı.

**S: Hava durumu neden yok?**  
C: EPİAŞ setinde sıcaklık yok; güneş üretimi dolaylı proxy. Future work: hava API.

**S: Production'da nasıl kullanırsınız?**  
C: Saatlik pipeline, önceki saat tüketimi + EPİAŞ üretim feed → model → tahmin; periyodik retrain.
