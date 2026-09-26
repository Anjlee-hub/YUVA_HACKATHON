"""
Production-Aware Multi-Variable Machine Learning Baseline Engine (ISO 50001 EnPI Compliant)
Fits an explainable Scikit-Learn regression model to predict expected energy and SEC 
based on multi-dimensional production, metallurgy, shift, and ambient variables.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from sklearn.linear_model import Ridge
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

class SECRegressionEngine:
    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        self.model: Optional[Pipeline] = None
        self.metrics: Dict[str, float] = {}
        self.feature_weights: Dict[str, float] = {}
        self.is_trained: bool = False
        self._train_baseline_model()

    def _generate_synthetic_historical_training_set(self, n_samples: int = 750) -> pd.DataFrame:
        """
        Generates 750 shifts (~250 days) of realistic baseline operational records
        for Shakti Foundry (Furnace 01 Primary Induction Melter).
        Includes realistic industrial variance, metallurgy product grades, shift conditions,
        ambient temperature shifts, and cold-start penalties.
        """
        np.random.seed(self.random_seed)
        
        production_tons = np.random.uniform(8.0, 32.0, n_samples)
        product_types = np.random.choice(
            ["Grey Iron (FG 260)", "SG / Ductile Iron (EN-GJS-500)", "Alloy Steel Castings"],
            n_samples, 
            p=[0.55, 0.35, 0.10]
        )
        shifts = np.random.choice(
            ["Shift A (06:00-14:00)", "Shift B (14:00-22:00)", "Night Shift (22:00-06:00)"],
            n_samples, 
            p=[0.40, 0.40, 0.20]
        )
        ambient_temps = np.random.normal(28.5, 4.2, n_samples).clip(18.0, 42.0)
        cold_starts = np.random.choice([0, 1], n_samples, p=[0.88, 0.12])
        runtime_hrs = np.random.uniform(6.5, 8.5, n_samples)
        
        product_sec_coeffs = {
            "Grey Iron (FG 260)": 570.0,
            "SG / Ductile Iron (EN-GJS-500)": 630.0,
            "Alloy Steel Castings": 680.0
        }
        shift_coeffs = {
            "Shift A (06:00-14:00)": 1.0,
            "Shift B (14:00-22:00)": 1.02,
            "Night Shift (22:00-06:00)": 0.98
        }
        
        energy_kwh = []
        for i in range(n_samples):
            p_sec = product_sec_coeffs[product_types[i]]
            s_mult = shift_coeffs[shifts[i]]
            c_penalty = 350.0 if cold_starts[i] == 1 else 0.0
            
            # Thermodynamic idle holding loss (85 kW coil holding power)
            active_hrs = min(runtime_hrs[i], production_tons[i] * 0.32)
            idle_hrs = max(0.2, runtime_hrs[i] - active_hrs)
            idle_kwh = 85.0 * idle_hrs
            
            # Ambient cooling penalty above 28°C
            weather_overhead = max(0.0, ambient_temps[i] - 28.0) * 1.2
            
            # Natural meter calibration / electrical noise (+- 12 kWh)
            noise = np.random.normal(0, 12.0)
            
            total_kwh = (production_tons[i] * p_sec * s_mult) + c_penalty + idle_kwh + weather_overhead + noise
            energy_kwh.append(round(total_kwh, 2))
            
        return pd.DataFrame({
            "production_tons": production_tons,
            "product_type": product_types,
            "shift": shifts,
            "ambient_temp_c": ambient_temps,
            "is_cold_start": cold_starts,
            "runtime_hrs": runtime_hrs,
            "energy_kwh": energy_kwh
        })

    def _train_baseline_model(self):
        """Fits an explainable Scikit-Learn Ridge Regression Pipeline."""
        df = self._generate_synthetic_historical_training_set()
        
        num_features = ["production_tons", "ambient_temp_c", "runtime_hrs", "is_cold_start"]
        cat_features = ["product_type", "shift"]
        
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), num_features),
                ("cat", OneHotEncoder(drop="first", sparse_output=False), cat_features)
            ]
        )
        
        self.model = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", Ridge(alpha=1.0))
        ])
        
        X = df.drop(columns=["energy_kwh"])
        y = df["energy_kwh"]
        
        self.model.fit(X, y)
        preds = self.model.predict(X)
        
        r2 = float(r2_score(y, preds))
        mae = float(mean_absolute_error(y, preds))
        rmse = float(root_mean_squared_error(y, preds))
        
        self.metrics = {
            "r2_score": round(r2, 4),
            "mae_kwh": round(mae, 2),
            "rmse_kwh": round(rmse, 2),
            "training_samples": len(df),
            "algorithm": "Scikit-Learn Ridge Regression with Standardized Features"
        }
        
        # Extract explainable feature importances
        ridge = self.model.named_steps["regressor"]
        cat_encoder = self.model.named_steps["preprocessor"].named_transformers_["cat"]
        cat_names = list(cat_encoder.get_feature_names_out(cat_features))
        all_feature_names = num_features + cat_names
        
        self.feature_weights = {
            name: round(float(weight), 2)
            for name, weight in zip(all_feature_names, ridge.coef_)
        }
        self.is_trained = True

    def predict_expected_energy(
        self,
        production_tons: float,
        product_type: str = "Grey Iron (FG 260)",
        shift: str = "Shift A (06:00-14:00)",
        ambient_temp_c: float = 28.5,
        is_cold_start: bool = False,
        runtime_hrs: float = 8.0
    ) -> Dict[str, Any]:
        """
        Predicts production-aware expected baseline energy (kWh) and expected SEC (kWh/ton)
        using the trained Scikit-Learn ML regression model with uncertainty bands.
        """
        if not self.is_trained or self.model is None:
            self._train_baseline_model()
            
        row = pd.DataFrame([{
            "production_tons": float(production_tons),
            "product_type": str(product_type),
            "shift": str(shift),
            "ambient_temp_c": float(ambient_temp_c),
            "is_cold_start": 1 if is_cold_start else 0,
            "runtime_hrs": float(runtime_hrs)
        }])
        
        pred_kwh = float(self.model.predict(row)[0])
        pred_kwh = max(100.0, pred_kwh) # Physical lower bound
        expected_sec = pred_kwh / max(0.1, production_tons)
        
        # 95% confidence prediction interval (± 1.96 * RMSE)
        margin = 1.96 * self.metrics.get("rmse_kwh", 250.0)
        
        return {
            "expected_kwh": round(pred_kwh, 2),
            "expected_sec": round(expected_sec, 2),
            "ci_lower_kwh": round(max(0.0, pred_kwh - margin), 2),
            "ci_upper_kwh": round(pred_kwh + margin, 2),
            "model_r2": self.metrics["r2_score"],
            "model_algorithm": self.metrics["algorithm"],
            "methodology": "Production-Aware Multi-Variable Scikit-Learn Regression",
            "is_ml_derived": True
        }

# Singleton instance
sec_ml_engine = SECRegressionEngine()
