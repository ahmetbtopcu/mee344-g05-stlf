# MEE344 Machine Learning — Grup G05 Final Raporu

## Türkiye Saatlik Elektrik Tüketim Tahmini (Decision Tree + AdaBoost)

**Ders:** MEE344 Machine Learning  
**Grup:** G05  
**Üyeler:** Berhan Kaya, Ahmet Bayram Topçu, Yusuf Duman, Furkan Efe Demirbel, Tekgül Eroğlu  
**Tarih:** 21 Mayıs 2026  
**Son teslim:** 22 Mayıs 2026, 17:00  

---

## 1. Yönetici Özeti

Bu proje, EPİAŞ Şeffaflık Platformu'ndan alınan gerçek zamanlı elektrik üretim ve tüketim verileri kullanılarak **saatlik elektrik tüketiminin (MWh) regresyon ile tahmin edilmesini** hedefler. Grup G05 için zorunlu modeller **Decision Tree** ve **AdaBoost** regresyonudur.

**Ana bulgular:**
- Veri penceresi: 31 Temmuz 2025 – 29 Ekim 2025 (2169 saat ham, 2001 saat feature sonrası).
- En iyi model: **AdaBoost** — Test RMSE **1040 MWh**, MAE **596 MWh**, R² **0.951**, MAPE **1.67%**.
- Decision Tree: Test RMSE **1311 MWh**, R² **0.923** — güçlü baseline, boosting ile iyileştirildi.
- Mevsimsel naive baseline (168h lag): RMSE 1489 MWh — ML modelleri belirgin üstün.

---

## 2. Giriş

### 2.1 STLF (Short-Term Load Forecasting)

Elektrik talep tahmini, üretim planlaması ve şebeke dengesinin saatlik/15 dakikalık ölçekte yönetilmesi için kritiktir. Bu projede **1 saatlik granülarite** ile tüketim tahmini yapılmıştır.

### 2.2 Proje kapsamı

Brief gereği tam ML iş akışı uygulanmıştır:
1. Problem tanımı ve veri anlama  
2. EDA ve preprocessing  
3. Feature engineering  
4. İki ML modeli (DT + AdaBoost) + baseline  
5. TimeSeriesSplit CV ve hold-out test  
6. Hiperparametre optimizasyonu  
7. Yorumlama ve pratik çıkarımlar  
8. Reproducible kod + README  

---

## 3. Veri Seti

### 3.1 Kaynak

| Dosya | İçerik |
|-------|--------|
| `Gercek_Zamanli_Uretim-31072025-29102025.csv` | Saatlik üretim kaynakları (16 kaynak + Toplam) |
| `Gercek_Zamanli_Tuketim-31072025-29102025.csv` | Saatlik tüketim (MWh) |

Kaynak: [EPİAŞ Şeffaflık Platformu](https://seffaflik.epias.com.tr)

### 3.2 Sütun sözlüğü (üretim)

| Sütun | Açıklama |
|-------|----------|
| Toplam | Toplam üretim (MWh) — **target yapılmadı** (kaynakların toplamı, leakage riski) |
| Doğal Gaz, Barajlı, Linyit, … | Kaynak bazlı üretim (MWh) — feature |
| Uluslararası | İthal/ihracat dengesi (negatif = ihracat) |

### 3.3 Hedef değişken

**`consumption_mwh`** — Tüketim Miktarı (MWh). Regresyon görevi; sürekli pozitif değerler.

### 3.4 Veri kapsamı

- Ham birleşik kayıt: **2169** saat  
- Feature engineering sonrası: **2001** saat (lag/rolling nedeniyle ilk 168 saat düşer)  
- Train: **1665** saat | Test: **336** saat (son ~14 gün, zaman bazlı split)

---

## 4. Keşifsel Veri Analizi (EDA)

Grafikler: `reports/figures/eda/`

### 4.1 Zaman serisi

Tüketim 40.000–57.000 MWh bandında; belirgin **günlük siklus** (gece düşük, akşam 18–21 pik) ve **haftalık fark** gözlenir.

### 4.2 Günlük profil

Saat 0–6 arası minimum; 09–12 ve 17–21 arası yükseliş. Standart sapma akşam saatlerinde genişler.

### 4.3 Üretim karışımı

Doğal gaz ve ithal kömür termik üretimde baskın; rüzgar ve güneş gün içi değişken. Yenilenebilir pay (`prod_renewable_share`) tüketimle kısmen korelasyonlu.

### 4.4 ACF

Lag 24 ve 168'de güçlü otokorelasyon — `lag_24h` ve `lag_168h` feature seçimini destekler.

### 4.5 Eksik değer

EPİAŞ verisinde eksik saat minimal; reindex sonrası kısa gap'ler forward-fill (max 2 saat).

---

## 5. Veri Ön İşleme

1. **Locale parsing:** `;` ayraç, `,` ondalık, `.` binlik ayracı (tarih sütunu korunarak).  
2. **Datetime:** `%d.%m.%Y %H:%M` birleştirme.  
3. **Saatlik reindex:** Eksik saatler tespit, ≤2 saat gap forward-fill.  
4. **Outlier:** Tüketim için 3×IQR clip (sadece target).  
5. **Düşük varyans:** `nafta`, `lng` çoğunlukla 0 → düşürüldü.

---

## 6. Feature Engineering

### 6.1 Zaman (cyclic)

$$\text{hour\_sin} = \sin(2\pi \cdot h / 24),\quad \text{hour\_cos} = \cos(2\pi \cdot h / 24)$$

Benzer şekilde `dow_sin/cos`, `doy_sin/cos`. Binary: `is_weekend`, `is_business_hour`, `is_holiday` (30 Ağustos, 29 Ekim).

### 6.2 Lag (target leakage önleme)

`lag_1h`, `lag_2h`, `lag_3h`, `lag_24h`, `lag_168h` — tüketim geçmişi.

### 6.3 Rolling (shift(1) ile)

`roll_mean_24h`, `roll_mean_168h`, `roll_std_24h`, `roll_max_24h`, `roll_min_24h`

### 6.4 Exogenous (üretim)

- `prod_wind`, `prod_solar`, `prod_hydro`, `prod_thermal`  
- `prod_renewable_share`  
- `net_balance = production_total - consumption`

**Toplam 26 feature** kullanıldı.

---

## 7. Modeller

### 7.1 Baseline'lar

| Model | Tanım |
|-------|--------|
| Baseline-1 | $y_t = y_{t-1}$ (son saat) |
| Baseline-2 | $y_t = y_{t-168}$ (geçen hafta aynı saat) |

### 7.2 Decision Tree Regressor

Tek karar ağacı; non-linear ilişkileri yakalar, yorumlanabilir.

**En iyi hiperparametreler (GridSearchCV, TimeSeriesSplit 5):**
- `max_depth=8`, `min_samples_leaf=2`, `min_samples_split=2`, `max_features=None`
- **CV RMSE:** 1472.50 MWh

### 7.3 AdaBoost Regressor

Zayıf öğrenici: `DecisionTreeRegressor(max_depth=8)` stump'ları; sıralı ağırlık güncellemesi ile residual düzeltme.

**En iyi hiperparametreler:**
- `n_estimators=200`, `learning_rate=1.0`, `loss=square`, `estimator__max_depth=8`
- **CV RMSE:** 1079.33 MWh

---

## 8. Değerlendirme Metodolojisi

- **CV:** `TimeSeriesSplit(n_splits=5)` — gelecek veriye leakage yok.  
- **Test:** Son 336 saat hold-out.  
- **Metrikler:** RMSE, MAE, R², MAPE, sMAPE (MWh ve %).

---

## 9. Sonuçlar

### 9.1 Test seti metrikleri

| Model | RMSE | MAE | R² | MAPE (%) |
|-------|------|-----|-----|----------|
| Baseline (1h) | 1498 | 1162 | 0.899 | 3.19 |
| Baseline (168h) | 1489 | 888 | 0.900 | 2.49 |
| Decision Tree | 1311 | 833 | 0.923 | 2.38 |
| **AdaBoost** | **1040** | **596** | **0.951** | **1.67** |

### 9.2 Karşılaştırma yorumu

- AdaBoost, DT'ye göre RMSE'de **~21%** iyileşme (1311 → 1040 MWh).  
- Her iki ML modeli, naive baseline'ları geçer.  
- R² 0.95 → test penceresinde yüksek açıklayıcılık; lag feature'ların güçlü sinyal taşıması beklenen sonuç.

Grafikler: `reports/figures/model/`, `reports/figures/interpretation/`

---

## 10. Tartışma ve Yorumlama

### 10.1 Feature importance

Permutation importance ve tree importance uyumlu: **lag_24h**, **lag_168h**, **hour_sin/cos**, **roll_mean_24h** en üst sıralarda.

### 10.2 Partial dependence

- `lag_24h`: güçlü pozitif monotonik ilişki.  
- `prod_solar`: gündüz üretim artışı tüketimle ilişkili (endüstriyel aktivite proxy).  

### 10.3 Hata analizi

- Artık hata akşam saatlerinde (18–21) daha yüksek — pik saatlerde model zorlanır.  
- Tatil günlerinde (30 Ağustos, 29 Ekim) sapma artabilir.  

### 10.4 Pratik anlam

Ortalama tüketim ~50.000 MWh/saat için %1.67 MAPE ≈ **840 MWh/saat** ortalama mutlak hata — operasyonel planlama için kabul edilebilir kısa vadeli tahmin bandı.

---

## 11. Sınırlılıklar

1. **Hava sıcaklığı yok** — sadece güneş üretimi dolaylı proxy.  
2. **3 aylık pencere** — tam yıllık mevsimsellik yakalanamaz.  
3. **Manuel tatil listesi** — tüm resmi tatiller eklenmemiş olabilir.  
4. **Lag feature'lar** — gerçek zamanlı tahminde önceki saat tüketimi gerekir (operasyonel kısıt).

---

## 12. Gelecek Çalışmalar

- Hava durumu API entegrasyonu (sıcaklık, nem).  
- XGBoost / LightGBM / LSTM karşılaştırması.  
- Ensemble (DT + AdaBoost + linear).  
- 15 dakikalık granülarite ve daha uzun eğitim penceresi.

---

## 13. Sonuç

G05 projesi, EPİAŞ verisi üzerinde uçtan uca STLF pipeline'ı başarıyla uygulamıştır. **AdaBoost**, allocation gereği **Decision Tree** ile birlikte en iyi performansı göstermiş; boosting'in residual düzeltme yaklaşımı saatlik tüketim tahmininde etkili olmuştur. Tüm kod, metrikler ve görseller `mee344-g05-stlf/` deposunda reproducible şekilde sunulmuştur.

---

## 14. Kaynaklar

1. EPİAŞ Şeffaflık Platformu — Gerçek Zamanlı Üretim/Tüketim verileri.  
2. Freund, Y., & Schapire, R. E. (1997). A decision-theoretic generalization of on-line learning and an application to boosting.  
3. scikit-learn documentation: DecisionTreeRegressor, AdaBoostRegressor, TimeSeriesSplit.  
4. MEE344 Project Brief (2026) — Regression, RMSE/MAE/R², grup projesi rubriği.

---

## Ek A: Parametre gridleri

**Decision Tree:** max_depth ∈ {3,5,8,12,16,None}, min_samples_split ∈ {2,5,10,20}, min_samples_leaf ∈ {1,2,5,10}, max_features ∈ {None, sqrt, 0.7}

**AdaBoost:** estimator__max_depth ∈ {3,5,8}, n_estimators ∈ {50,100,200}, learning_rate ∈ {0.05,0.1,0.5,1.0}, loss ∈ {linear, square}

---

## Ek B: Çalıştırma

```bash
py -3 scripts/01_build_dataset.py
py -3 scripts/run_eda.py
py -3 scripts/02_train_decision_tree.py
py -3 scripts/03_train_adaboost.py
py -3 scripts/04_evaluate_all.py
py -3 scripts/run_interpretation.py
py -3 scripts/05_export_slide_assets.py
py -3 scripts/build_pptx.py
```
