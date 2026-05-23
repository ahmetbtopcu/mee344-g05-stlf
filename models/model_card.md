# Model Cards — G05 STLF

## Decision Tree Regressor

| Alan | Değer |
|------|--------|
| **Görev** | Saatlik tüketim regresyonu |
| **Eğitim verisi** | 1665 saat (31.07–mid Ekim 2025) |
| **Feature sayısı** | 26 |
| **CV RMSE** | 1472.50 MWh |
| **Test RMSE** | 1311.21 MWh |
| **Test R²** | 0.923 |
| **Best params** | max_depth=8, min_samples_leaf=2, min_samples_split=2 |
| **Varsayım** | Geçmiş lag değerleri tahmin anında mevcut |
| **Kısıt** | Tek ağaç — yüksek varyans riski (CV ile sınırlandı) |

## AdaBoost Regressor

| Alan | Değer |
|------|--------|
| **Görev** | Saatlik tüketim regresyonu |
| **Base estimator** | DecisionTreeRegressor(max_depth=8) |
| **CV RMSE** | 1079.33 MWh |
| **Test RMSE** | 1040.03 MWh |
| **Test R²** | 0.951 |
| **Test MAPE** | 1.67% |
| **Best params** | n_estimators=200, learning_rate=1.0, loss=square |
| **Varsayım** | Sıralı boosting; train dağılımı teste benzer |
| **Kısıt** | Out-of-sample uzun horizon belirsiz |

## Inference

```python
import joblib
bundle = joblib.load("models/adaboost.joblib")
pred = bundle["model"].predict(X[bundle["feature_columns"]])
```
