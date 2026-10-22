import sys
import os
import numpy as np

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

from app.db.session import SessionLocal
from app.models import Dispute, Order, Payment, FulfilmentRecord, CustomerMessage, AIInvestigation, DisputeStatus
from app.scoring.pipeline import ExplainableScoringPipeline


def main():
    print("Training and evaluating Explainable Dispute Win-Score model...")
    db = SessionLocal()
    pipeline = ExplainableScoringPipeline()

    try:
        disputes = db.query(Dispute).all()
        if not disputes:
            print("No disputes found in database! Please run scripts/seed_db.py first.")
            return

        X = []
        y = []

        for d in disputes:
            order = db.query(Order).filter(Order.id == d.order_id).first()
            payment = db.query(Payment).filter(Payment.id == d.payment_id).first()
            fulfilment = db.query(FulfilmentRecord).filter(FulfilmentRecord.order_id == d.order_id).first()
            messages = db.query(CustomerMessage).filter(CustomerMessage.order_id == d.order_id).all()
            inv = db.query(AIInvestigation).filter(AIInvestigation.dispute_id == d.id).first()

            feats = pipeline.extract_features(d, order, payment, fulfilment, messages, inv)
            X.append(feats)

            # Ground truth label: 1 if won or win score >= 65, else 0
            label = 1 if d.status == DisputeStatus.WON or (d.win_probability_score and d.win_probability_score >= 60.0) else 0
            y.append(label)

        X_arr = np.array(X)
        y_arr = np.array(y)

        metrics = pipeline.train_and_evaluate(X_arr, y_arr)
        print("\n--- Model Training & Evaluation Results ---")
        print(f"Model: {metrics['model_name']} (v{metrics['version']})")
        print(f"Total Samples: {metrics['sample_size']} (Train: {metrics['train_size']}, Test: {metrics['test_size']})")
        print(f"Accuracy:  {metrics['accuracy']:.1%}")
        print(f"Precision: {metrics['precision']:.1%}")
        print(f"Recall:    {metrics['recall']:.1%}")
        print(f"F1 Score:  {metrics['f1_score']:.3f}")
        print(f"ROC-AUC:   {metrics['roc_auc']:.3f}")
        print(f"Brier:     {metrics['brier_score']:.3f}")
        print(f"Confusion Matrix: {metrics['confusion_matrix']}")
        print(f"\nArtifacts saved to backend/app/scoring/model.joblib and metrics.json.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
