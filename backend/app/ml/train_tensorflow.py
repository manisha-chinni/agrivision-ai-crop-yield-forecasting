"""Train a small optional TensorFlow regressor using seeded synthetic data only."""
from pathlib import Path
import numpy as np
from .model import _synthetic_training_data

def train(output: Path | None = None):
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise SystemExit("TensorFlow is optional. Install it with: pip install tensorflow") from exc
    tf.keras.utils.set_random_seed(2025)
    x, y = _synthetic_training_data()
    rng = np.random.default_rng(42)
    order = rng.permutation(len(y))
    split = int(.8 * len(y))
    train_ids, test_ids = order[:split], order[split:]
    normalizer = tf.keras.layers.Normalization(axis=-1)
    normalizer.adapt(x[train_ids].astype("float32"))
    model = tf.keras.Sequential([normalizer, tf.keras.layers.Dense(32, activation="relu"), tf.keras.layers.Dense(16, activation="relu"), tf.keras.layers.Dense(1)])
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=.003), loss="mse", metrics=["mae"])
    model.fit(x[train_ids].astype("float32"), y[train_ids].astype("float32"), validation_data=(x[test_ids].astype("float32"), y[test_ids].astype("float32")), epochs=40, batch_size=32, verbose=0, callbacks=[tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)])
    target = output or Path(__file__).resolve().parents[3] / "models" / "tensorflow_synthetic_demo.keras"
    target.parent.mkdir(parents=True, exist_ok=True)
    model.save(target)
    prediction = model.predict(x[test_ids].astype("float32"), verbose=0).reshape(-1)
    mae = float(np.mean(np.abs(prediction-y[test_ids])))
    print(f"Saved synthetic-demo model to {target}; synthetic holdout MAE={mae:.3f} tons/ha")
    return target, mae

if __name__ == "__main__":
    train()
