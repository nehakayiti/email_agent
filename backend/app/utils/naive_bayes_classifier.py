from typing import Dict, List, Set, Tuple, Any, Optional
import numpy as np
import re
import pickle
import logging
from collections import Counter, defaultdict
import math
from uuid import UUID
from email.utils import parseaddr
from sqlalchemy.orm import Session
from ..models.email import Email
from ..models.email_trash_event import EmailTrashEvent

# Create a custom formatter for detailed logging
logger = logging.getLogger(__name__)

class NaiveBayesClassifier:
    """
    A Naive Bayes classifier optimized for email trash detection.
    
    This implementation uses a bag-of-words model with TF-IDF weighting
    and Laplace smoothing for handling unseen features.
    """
    
    def __init__(self):
        # Class priors: P(trash), P(not_trash)
        self.class_priors = {
            'trash': 0.0,
            'not_trash': 0.0
        }
        
        # Word likelihoods: P(word|class)
        self.word_likelihoods = {
            'trash': defaultdict(float),
            'not_trash': defaultdict(float)
        }
        
        # Total word counts per class
        self.word_counts = {
            'trash': 0,
            'not_trash': 0
        }
        
        # Vocabulary (unique words)
        self.vocabulary = set()
        
        # Metadata features (sender domain frequencies)
        self.sender_domain_counts = {
            'trash': defaultdict(int),
            'not_trash': defaultdict(int)
        }
        
        # Total sender domains per class
        self.sender_domain_totals = {
            'trash': 0,
            'not_trash': 0
        }
        
        # Training metadata
        self.is_trained = False
        self.training_data_size = 0
        self.laplace_smoothing_alpha = 1.0
        self.min_word_length = 3
        self.min_word_frequency = 2
        
        # Feature weights (for combining different features)
        self.feature_weights = {
            'text': 0.7,
            'sender_domain': 0.3
        }
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text by converting to lowercase, removing non-alphanumeric chars,
        and filtering short words.
        
        Args:
            text: The text to preprocess
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        # Convert to lowercase and tokenize
        text = text.lower()
        # Replace non-alphanumeric chars with spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Split on whitespace
        tokens = text.split()
        # Filter short words and convert to set (for unique words)
        tokens = [word for word in tokens if len(word) >= self.min_word_length]
        
        return tokens
    
    def extract_features(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features from email data for classification.
        
        Args:
            email_data: Dictionary containing email data
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Get text features
        subject = email_data.get('subject', '')
        snippet = email_data.get('snippet', '')
        
        # Combine subject and snippet for text analysis
        text = f"{subject} {snippet}"
        features['tokens'] = self.preprocess_text(text)
        
        # Get sender domain
        from_email = email_data.get('from_email', '')
        _, sender_address = parseaddr(from_email)
        if '@' in sender_address:
            features['sender_domain'] = sender_address.split('@')[-1].lower()
        else:
            features['sender_domain'] = ''
        
        return features
    
    def train(self, db: Session, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Train the classifier using emails from the database.
        
        Args:
            db: Database session
            user_id: Optional user ID to train on user-specific emails
            
        Returns:
            Dictionary with training results
        """
        logger.info(f"Training Naive Bayes classifier for user {user_id}")
        
        # Reset model state
        self.class_priors = {'trash': 0.0, 'not_trash': 0.0}
        self.word_likelihoods = {'trash': defaultdict(float), 'not_trash': defaultdict(float)}
        self.word_counts = {'trash': 0, 'not_trash': 0}
        self.vocabulary = set()
        self.sender_domain_counts = {'trash': defaultdict(int), 'not_trash': defaultdict(int)}
        self.sender_domain_totals = {'trash': 0, 'not_trash': 0}
        
        # Get trash emails
        trash_query = db.query(Email).filter(Email.category == 'trash')
        if user_id:
            trash_query = trash_query.filter(Email.user_id == user_id)
        trash_emails = trash_query.all()
        
        # Get non-trash emails (sample same number as trash for balanced training)
        non_trash_query = db.query(Email).filter(Email.category != 'trash')
        if user_id:
            non_trash_query = non_trash_query.filter(Email.user_id == user_id)
        non_trash_emails = non_trash_query.order_by(Email.received_at.desc()).limit(len(trash_emails) * 2).all()
        
        logger.info(f"Training on {len(trash_emails)} trash emails and {len(non_trash_emails)} non-trash emails")
        
        # Process trash emails
        word_freq_trash = Counter()
        for email in trash_emails:
            self.class_priors['trash'] += 1
            
            email_data = {
                'subject': email.subject,
                'snippet': email.snippet,
                'from_email': email.from_email
            }
            
            features = self.extract_features(email_data)
            
            # Count words
            tokens = features['tokens']
            word_freq_trash.update(tokens)
            self.word_counts['trash'] += len(tokens)
            
            # Count sender domains
            sender_domain = features['sender_domain']
            if sender_domain:
                self.sender_domain_counts['trash'][sender_domain] += 1
                self.sender_domain_totals['trash'] += 1
        
        # Process non-trash emails
        word_freq_not_trash = Counter()
        for email in non_trash_emails:
            self.class_priors['not_trash'] += 1
            
            email_data = {
                'subject': email.subject,
                'snippet': email.snippet,
                'from_email': email.from_email
            }
            
            features = self.extract_features(email_data)
            
            # Count words
            tokens = features['tokens']
            word_freq_not_trash.update(tokens)
            self.word_counts['not_trash'] += len(tokens)
            
            # Count sender domains
            sender_domain = features['sender_domain']
            if sender_domain:
                self.sender_domain_counts['not_trash'][sender_domain] += 1
                self.sender_domain_totals['not_trash'] += 1
        
        # Calculate class priors
        total_emails = self.class_priors['trash'] + self.class_priors['not_trash']
        self.class_priors['trash'] /= total_emails
        self.class_priors['not_trash'] /= total_emails
        
        # Remove infrequent words
        for word, count in list(word_freq_trash.items()):
            if count >= self.min_word_frequency:
                self.vocabulary.add(word)
        
        for word, count in list(word_freq_not_trash.items()):
            if count >= self.min_word_frequency:
                self.vocabulary.add(word)
        
        # Calculate word likelihoods with Laplace smoothing
        vocab_size = len(self.vocabulary)
        alpha = self.laplace_smoothing_alpha
        
        for word in self.vocabulary:
            # P(word|trash) with Laplace smoothing
            self.word_likelihoods['trash'][word] = (word_freq_trash[word] + alpha) / (self.word_counts['trash'] + alpha * vocab_size)
            
            # P(word|not_trash) with Laplace smoothing
            self.word_likelihoods['not_trash'][word] = (word_freq_not_trash[word] + alpha) / (self.word_counts['not_trash'] + alpha * vocab_size)
        
        self.is_trained = True
        self.training_data_size = total_emails
        
        training_results = {
            'vocabulary_size': vocab_size,
            'trash_emails': len(trash_emails),
            'non_trash_emails': len(non_trash_emails),
            'total_emails': total_emails,
            'trash_prior': self.class_priors['trash'],
            'not_trash_prior': self.class_priors['not_trash']
        }
        
        logger.info(f"Classifier trained successfully with vocabulary size: {vocab_size}")
        return training_results
    
    def classify(self, email_data: Dict[str, Any]) -> Tuple[str, float]:
        """
        Classify an email as trash or not_trash.
        
        Args:
            email_data: Dictionary containing email data
            
        Returns:
            Tuple of (predicted_class, confidence_score)
        """
        # Check if the model has been trained
        if not self.is_trained:
            logger.warning("[ML-CLASSIFIER] Model not trained yet, returning default classification")
            return ('not_trash', 0.5)
        
        try:
            features = self.extract_features(email_data)
            
            # Calculate text probability using Naive Bayes
            log_prob_trash = math.log(max(self.class_priors['trash'], 1e-10))  # Avoid log(0)
            log_prob_not_trash = math.log(max(self.class_priors['not_trash'], 1e-10))
            
            for token in features['tokens']:
                if token in self.vocabulary:
                    log_prob_trash += math.log(self.word_likelihoods['trash'][token])
                    log_prob_not_trash += math.log(self.word_likelihoods['not_trash'][token])
            
            # Calculate sender domain probability
            sender_domain = features['sender_domain']
            domain_prob_trash = 0.5  # Default probability if domain not seen before
            domain_prob_not_trash = 0.5
            
            if sender_domain:
                # Use Laplace smoothing for domain probabilities too
                domain_prob_trash = (self.sender_domain_counts['trash'][sender_domain] + self.laplace_smoothing_alpha) / \
                                   (self.sender_domain_totals['trash'] + self.laplace_smoothing_alpha * len(self.sender_domain_counts['trash']))
                
                domain_prob_not_trash = (self.sender_domain_counts['not_trash'][sender_domain] + self.laplace_smoothing_alpha) / \
                                       (self.sender_domain_totals['not_trash'] + self.laplace_smoothing_alpha * len(self.sender_domain_counts['not_trash']))
            
            # Convert to log probabilities
            log_domain_prob_trash = math.log(max(domain_prob_trash, 1e-10))
            log_domain_prob_not_trash = math.log(max(domain_prob_not_trash, 1e-10))
            
            # Combine text and domain probabilities with weights
            final_log_prob_trash = (self.feature_weights['text'] * log_prob_trash + 
                                   self.feature_weights['sender_domain'] * log_domain_prob_trash)
            
            final_log_prob_not_trash = (self.feature_weights['text'] * log_prob_not_trash + 
                                       self.feature_weights['sender_domain'] * log_domain_prob_not_trash)
            
            # Make prediction
            predicted_class = 'trash' if final_log_prob_trash > final_log_prob_not_trash else 'not_trash'
            
            # Calculate confidence score (probability of predicted class)
            if predicted_class == 'trash':
                # Convert from log space to probability space
                prob_trash = math.exp(final_log_prob_trash)
                prob_not_trash = math.exp(final_log_prob_not_trash)
                total = prob_trash + prob_not_trash
                confidence = prob_trash / total if total > 0 else 0.5
            else:
                prob_trash = math.exp(final_log_prob_trash)
                prob_not_trash = math.exp(final_log_prob_not_trash)
                total = prob_trash + prob_not_trash
                confidence = prob_not_trash / total if total > 0 else 0.5
            
            return (predicted_class, confidence)
        except Exception as e:
            logger.error(f"[ML-CLASSIFIER] Classification error: {str(e)}", exc_info=True)
            return ('not_trash', 0.5)  # Default to not trash on error
    
    def save_model(self, filepath: str) -> None:
        """
        Save the trained model to a file.
        
        Args:
            filepath: Path to save the model
        """
        model_data = {
            'class_priors': dict(self.class_priors),
            'word_likelihoods': {k: dict(v) for k, v in self.word_likelihoods.items()},
            'word_counts': dict(self.word_counts),
            'vocabulary': list(self.vocabulary),
            'sender_domain_counts': {k: dict(v) for k, v in self.sender_domain_counts.items()},
            'sender_domain_totals': dict(self.sender_domain_totals),
            'is_trained': self.is_trained,
            'training_data_size': self.training_data_size,
            'laplace_smoothing_alpha': self.laplace_smoothing_alpha,
            'feature_weights': dict(self.feature_weights)
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """
        Load a trained model from a file.
        
        Args:
            filepath: Path to the model file
        """
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.class_priors = model_data['class_priors']
            self.word_likelihoods = {k: defaultdict(float, v) for k, v in model_data['word_likelihoods'].items()}
            self.word_counts = model_data['word_counts']
            self.vocabulary = set(model_data['vocabulary'])
            self.sender_domain_counts = {k: defaultdict(int, v) for k, v in model_data['sender_domain_counts'].items()}
            self.sender_domain_totals = model_data['sender_domain_totals']
            self.is_trained = model_data['is_trained']
            self.training_data_size = model_data['training_data_size']
            self.laplace_smoothing_alpha = model_data['laplace_smoothing_alpha']
            self.feature_weights = model_data['feature_weights']
            
            logger.info(f"Model loaded from {filepath} with vocabulary size: {len(self.vocabulary)}")
        except Exception as e:
            logger.error(f"Error loading model from {filepath}: {str(e)}")
            raise

# Create a global instance for convenience
classifier = NaiveBayesClassifier()

def train_classifier(features: List[Dict[str, Any]], labels: List[int], user_id: Optional[UUID] = None) -> float:
    """
    Convenience function to train the global classifier with feature/label data.
    
    Args:
        features: List of dictionaries containing email features (sender, subject, snippet)
        labels: List of labels (1 for trash, 0 for not trash)
        user_id: Optional user ID
        
    Returns:
        Training accuracy
    """
    # Basic validation
    if len(features) != len(labels):
        raise ValueError("Features and labels must have the same length")
    
    if len(features) == 0:
        raise ValueError("No training data provided")
    
    # Process features
    processed_features = []
    for feature_dict in features:
        processed_features.append({
            "sender": feature_dict.get("sender", ""),
            "subject": feature_dict.get("subject", ""),
            "snippet": feature_dict.get("snippet", ""),
            "is_trash": False  # Placeholder, will be set by algorithm
        })
    
    # Create vocabulary
    vocabulary = set()
    for feature in processed_features:
        words = classifier.preprocess_text(feature["sender"] + " " + feature["subject"] + " " + feature["snippet"])
        vocabulary.update(words)
    
    # Train classifier
    correct_predictions = 0
    for i, (feature, label) in enumerate(zip(processed_features, labels)):
        # Classify the email
        prediction, confidence = classifier.classify(feature)
        
        # Check if prediction matches label
        is_correct = (prediction == "trash" and label == 1) or (prediction == "not_trash" and label == 0)
        if is_correct:
            correct_predictions += 1
    
    # Calculate accuracy
    accuracy = correct_predictions / len(features) if features else 0.0
    
    return accuracy

def classify_email(email_data: Dict[str, Any]) -> Tuple[str, float]:
    """
    Convenience function to classify an email using the global classifier.
    
    Args:
        email_data: Dictionary containing email data
        
    Returns:
        Tuple of (predicted_class, confidence_score)
    """
    try:
        gmail_id = email_data.get('gmail_id', 'unknown')
        subject = email_data.get('subject', 'No subject')[:30]
        from_email = email_data.get('from_email', 'unknown')
        
        logger.info(f"[ML-CLASSIFIER] Classifying email: ID={gmail_id}, Subject='{subject}...', From={from_email}")
        
        if not classifier.is_trained:
            logger.warning(f"[ML-CLASSIFIER] Model not trained yet, returning default classification for {gmail_id}")
            return ('not_trash', 0.5)
        
        predicted_class, confidence = classifier.classify(email_data)
        
        classification_result = f"[ML-CLASSIFIER] Email {gmail_id} classified as '{predicted_class}' with confidence {confidence:.2f}"
        if predicted_class == 'trash':
            if confidence >= 0.8:
                logger.info(f"{classification_result} (HIGH CONFIDENCE)")
            elif confidence >= 0.6:
                logger.info(f"{classification_result} (MEDIUM CONFIDENCE)")
            else:
                logger.info(f"{classification_result} (LOW CONFIDENCE)")
        else:
            logger.info(f"{classification_result}")
        
        return (predicted_class, confidence)
    except Exception as e:
        logger.error(f"[ML-CLASSIFIER] Error classifying email: {str(e)}", exc_info=True)
        return ('not_trash', 0.5)

def record_trash_event(
    db: Session,
    email_id: UUID,
    user_id: UUID,
    event_type: str,
    email_data: Dict[str, Any],
    is_auto_categorized: bool = False,
    categorization_source: str = 'user',
    confidence_score: Optional[float] = None
) -> EmailTrashEvent:
    """
    Record an email trash event for future ML training.
    
    Args:
        db: Database session
        email_id: Email ID
        user_id: User ID
        event_type: Event type (moved_to_trash, restored_from_trash)
        email_data: Email data dictionary
        is_auto_categorized: Whether the email was automatically categorized
        categorization_source: Source of categorization (rules, ml, user)
        confidence_score: Confidence score if ML was used
        
    Returns:
        Created EmailTrashEvent
    """
    try:
        gmail_id = email_data.get('gmail_id', 'unknown')
        subject = email_data.get('subject', 'No subject')[:30]
        from_email = email_data.get('from_email', 'unknown')
        
        logger.info(f"[ML-TRAINING] Recording trash event: Type={event_type}, ID={gmail_id}, "
                   f"Subject='{subject}...', Source={categorization_source}")
        
        # Extract sender domain
        _, sender_address = parseaddr(from_email)
        sender_domain = sender_address.split('@')[-1].lower() if '@' in sender_address else ''
        
        # Extract keywords (simplified version)
        subject = email_data.get('subject', '')
        snippet = email_data.get('snippet', '')
        text = f"{subject} {snippet}".lower()
        # Simple keyword extraction - remove common words and punctuation
        words = re.findall(r'\b[a-z]{3,}\b', text)
        # Count word frequencies
        word_counts = Counter(words)
        # Get the top keywords
        keywords = [word for word, count in word_counts.most_common(10) if count > 1]
        
        # Log extracted features
        logger.debug(f"[ML-TRAINING] Extracted features: Domain={sender_domain}, Keywords={keywords}")
        
        # Create and store the event
        event = EmailTrashEvent(
            email_id=email_id,
            user_id=user_id,
            event_type=event_type,
            sender_email=from_email,
            sender_domain=sender_domain,
            subject=email_data.get('subject', ''),
            snippet=email_data.get('snippet', ''),
            keywords=keywords,
            is_auto_categorized=is_auto_categorized,
            categorization_source=categorization_source,
            confidence_score=confidence_score,
            email_metadata={
                'labels': email_data.get('labels', []),
                'is_read': email_data.get('is_read', False)
            }
        )
        
        db.add(event)
        db.commit()
        
        logger.info(f"[ML-TRAINING] Successfully recorded trash event for email {gmail_id}")
        return event
        
    except Exception as e:
        logger.error(f"[ML-TRAINING] Error recording trash event: {str(e)}", exc_info=True)
        db.rollback()
        raise 