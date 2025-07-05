"""
Utilities for evaluating and cross-validating email classification models.
This module provides functions for comprehensive model evaluation beyond simple accuracy.
"""
import logging
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from uuid import UUID
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score
from sklearn.model_selection import KFold
from .naive_bayes_classifier import classify_email, load_classifier_model

logger = logging.getLogger(__name__)

def evaluate_model_detailed(
    features: List[Dict[str, Any]], 
    labels: List[int], 
    user_id: Optional[UUID] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Evaluate a trained model with comprehensive metrics
    
    Args:
        features: List of feature dictionaries (email data)
        labels: Ground truth labels (1 for trash, 0 for not_trash)
        user_id: Optional user ID for user-specific model
        verbose: Whether to log detailed results
        
    Returns:
        Dictionary with detailed evaluation metrics
    """
    # Make predictions
    predictions = []
    probabilities = []
    
    logger.info(f"Evaluating model on {len(features)} samples...")
    
    for feature in features:
        email_data = {
            "from_email": feature.get("sender", ""),
            "subject": feature.get("subject", ""),
            "snippet": feature.get("snippet", ""),
            "gmail_id": feature.get("gmail_id", "unknown")
        }
        
        prediction, confidence = classify_email(email_data, user_id)
        pred_label = 1 if prediction == "trash" else 0
        predictions.append(pred_label)
        probabilities.append(confidence if pred_label == 1 else 1 - confidence)
    
    # Convert to numpy arrays
    y_true = np.array(labels)
    y_pred = np.array(predictions)
    y_prob = np.array(probabilities)
    
    # Calculate standard metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    # Calculate confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    # Calculate specificity (true negative rate)
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    
    # Calculate ROC AUC if we have valid probabilities
    try:
        auc = roc_auc_score(y_true, y_prob)
    except:
        auc = 0
        logger.warning("Could not calculate AUC - check probability estimates")
    
    # Create classification report
    report = classification_report(y_true, y_pred, output_dict=True)
    
    # Log detailed results if requested
    if verbose:
        logger.info(f"Model Evaluation Results (samples: {len(features)})")
        logger.info(f"Accuracy: {accuracy:.4f}")
        logger.info(f"Precision: {precision:.4f}")
        logger.info(f"Recall: {recall:.4f}")
        logger.info(f"F1 Score: {f1:.4f}")
        logger.info(f"Specificity: {specificity:.4f}")
        logger.info(f"AUC: {auc:.4f}")
        logger.info(f"Confusion Matrix: \n{cm}")
        logger.info(f"True Positives: {tp}, False Positives: {fp}")
        logger.info(f"True Negatives: {tn}, False Negatives: {fn}")
    
    # Return comprehensive metrics
    results = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "specificity": specificity,
        "auc": auc,
        "confusion_matrix": cm.tolist(),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
        "samples_count": len(features),
        "classification_report": report
    }
    
    return results

def perform_cross_validation(
    features: List[Dict[str, Any]], 
    labels: List[int],
    user_id: Optional[UUID] = None,
    n_folds: int = 5
) -> Dict[str, Any]:
    """
    Perform cross-validation using KFold
    
    Args:
        features: List of feature dictionaries (email data)
        labels: Ground truth labels (1 for trash, 0 for not_trash)
        user_id: Optional user ID for user-specific model
        n_folds: Number of cross-validation folds
        
    Returns:
        Dictionary with cross-validation results
    """
    from .naive_bayes_classifier import train_classifier
    
    logger.info(f"Performing {n_folds}-fold cross-validation...")
    
    # Initialize metrics storage
    all_metrics = []
    
    # Create KFold cross-validator
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)
    
    # Array of labels
    y = np.array(labels)
    
    fold = 1
    for train_idx, test_idx in kf.split(features):
        logger.info(f"Fold {fold}/{n_folds}")
        
        # Split data
        X_train = [features[i] for i in train_idx]
        y_train = y[train_idx].tolist()
        X_test = [features[i] for i in test_idx]
        y_test = y[test_idx].tolist()
        
        # Train model on this fold
        train_accuracy = train_classifier(X_train, y_train, user_id)
        logger.info(f"Fold {fold} - Training accuracy: {train_accuracy:.4f}")
        
        # Evaluate on test data
        metrics = evaluate_model_detailed(X_test, y_test, user_id, verbose=False)
        logger.info(f"Fold {fold} - Test accuracy: {metrics['accuracy']:.4f}, F1: {metrics['f1']:.4f}")
        
        # Add fold number to metrics
        metrics["fold"] = fold
        all_metrics.append(metrics)
        
        fold += 1
    
    # Calculate average metrics across folds
    avg_accuracy = np.mean([m["accuracy"] for m in all_metrics])
    avg_precision = np.mean([m["precision"] for m in all_metrics])
    avg_recall = np.mean([m["recall"] for m in all_metrics])
    avg_f1 = np.mean([m["f1"] for m in all_metrics])
    avg_specificity = np.mean([m["specificity"] for m in all_metrics])
    
    # Calculate standard deviations
    std_accuracy = np.std([m["accuracy"] for m in all_metrics])
    std_precision = np.std([m["precision"] for m in all_metrics])
    std_recall = np.std([m["recall"] for m in all_metrics])
    std_f1 = np.std([m["f1"] for m in all_metrics])
    
    logger.info(f"Cross-validation complete.")
    logger.info(f"Avg Accuracy: {avg_accuracy:.4f} ± {std_accuracy:.4f}")
    logger.info(f"Avg Precision: {avg_precision:.4f} ± {std_precision:.4f}")
    logger.info(f"Avg Recall: {avg_recall:.4f} ± {std_recall:.4f}")
    logger.info(f"Avg F1: {avg_f1:.4f} ± {std_f1:.4f}")
    
    # Return all metrics
    return {
        "average_metrics": {
            "accuracy": float(avg_accuracy),
            "precision": float(avg_precision),
            "recall": float(avg_recall),
            "f1": float(avg_f1),
            "specificity": float(avg_specificity),
            "accuracy_std": float(std_accuracy),
            "precision_std": float(std_precision),
            "recall_std": float(std_recall),
            "f1_std": float(std_f1)
        },
        "fold_metrics": all_metrics,
        "n_folds": n_folds,
        "samples_count": len(features)
    } 