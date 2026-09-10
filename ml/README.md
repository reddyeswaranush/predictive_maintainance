# FactoryOps predictive-maintenance models

The default prediction endpoint uses two `XGBRegressor` models trained from
the telemetry features in `ml.features`: one for failure probability and one
for health score. XGBoost operates directly on the generated features, so no
feature scaling is applied. The models and their metadata are saved by:

```powershell
.\.venv\Scripts\python.exe -m ml.train_model
```

The default artifact is saved to `ml\model.json`, with the two native XGBoost
model files saved beside it. `predicted_days` remains a derived value based on
the predicted failure probability.

## MetroPT-3 machine-failure model

The production training pipeline uses the uploaded MetroPT-3 Air Compressor
CSV. It reads the 1-second stream in chunks, aggregates it to one-minute
records, creates causal rolling features, and labels the 24 hours before each
documented failure as `failure imminent`.

## Train and evaluate

Run these commands from the project root:

```powershell
.\.venv\Scripts\python.exe -m ml.metropt_pipeline train
.\.venv\Scripts\python.exe -m ml.metropt_pipeline evaluate
```

The trained artifact is saved to `ml\metropt_model.joblib`.

The four event windows are stored in the artifact metadata. Evaluation is
leave-one-failure-event-out and reports ROC-AUC and PR-AUC. Because MetroPT-3
contains one compressor and only four documented failures, these metrics are
research/prototype measurements, not production reliability guarantees.

## API inference

`POST /predictions/generate-metro` accepts one MetroPT-3 reading and stores the
result in the existing predictions table. It returns:

- `failure_probability`: probability of failure within the next 24 hours
- `health_score`: `100 * (1 - failure_probability)`
- `predicted_days`: a short warning-horizon estimate from 1 to 7 days; this is
  not a directly supervised RUL target because MetroPT-3 does not provide RUL.
