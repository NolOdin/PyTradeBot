# ml_learner.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
from data_manager import DataManager

class MLLearner:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.dm = DataManager()

    def prepare_data(self):
        df = self.dm.get_history()
        if len(df) < 10:
            return None, None
        df['price_diff'] = df['price'].pct_change()
        df['target'] = (df['profit_loss'] > 0).astype(int)
        df = df.dropna()
        X = df[['price_diff', 'signal_strength']]
        y = df['target']
        return X, y

    def train(self):
        X, y = self.prepare_data()
        if X is None:
            return
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        self.model.fit(X_train, y_train)
        acc = accuracy_score(y_test, self.model.predict(X_test))
        print(f"[ML] Accuracy: {acc:.2f}")

    def predict_efficiency(self, price_diff, signal_strength):
        self.train()
        try:
            prob = self.model.predict_proba([[price_diff, signal_strength]])[0][1]
            return prob > 0.6
        except:
            return False
