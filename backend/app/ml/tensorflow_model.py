"""Optional TensorFlow inference adapter; the demo API uses the sklearn baseline."""
from pathlib import Path

class TensorFlowYieldModel:
    def __init__(self, model_path: str | Path):
        try:
            import tensorflow as tf
        except ImportError as exc:
            raise RuntimeError("TensorFlow is optional and is not installed. Install tensorflow to load this model.") from exc
        path = Path(model_path)
        if not path.is_file():
            raise RuntimeError(f"TensorFlow model file not found: {path}")
        self._tf = tf
        self.model = tf.keras.models.load_model(path)

    def predict(self, feature_matrix):
        import numpy as np
        values = np.asarray(feature_matrix, dtype="float32")
        if values.ndim != 2:
            raise ValueError("Expected a two-dimensional feature matrix")
        return self.model.predict(values, verbose=0).reshape(-1)
