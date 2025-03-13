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
from datetime import datetime, timezone

# Create a custom formatter for detailed logging
logger = logging.getLogger(__name__)

# Helper function to extract domain from email address
def extract_domain(email_address: str) -> str:
    """
    Extract the domain part from an email address.
    
    Args:
        email_address: Email address to extract domain from
        
    Returns:
        Domain or empty string if no valid domain found
    """
    _, address = parseaddr(email_address)
    if '@' in address:
        return address.split('@')[-1].lower()
    return ''

# Model cache - store loaded models keyed by user_id (None for global)
_model_cache = {}
# Track when models were last loaded
_model_load_time = {}
# Cache TTL in seconds (10 minutes)
_MODEL_CACHE_TTL = 600

# Stopwords to filter out common English words that don't add value for classification
STOPWORDS = {
    'the', 'and', 'a', 'to', 'of', 'is', 'in', 'that', 'it', 'with', 'for', 'as', 'on', 'at', 'this', 
    'by', 'be', 'are', 'or', 'an', 'not', 'from', 'but', 'was', 'were', 'they', 'their', 'you', 'your',
    'has', 'have', 'had', 'can', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
    'me', 'my', 'mine', 'we', 'us', 'our', 'ours', 'his', 'her', 'hers', 'its', 'their', 'theirs',
    'out', 'get', 'go', 'use', 'been', 'being', 'some', 'there', 'then', 'than', 'all', 'one', 'two',
    'who', 'when', 'where', 'which', 'what', 'why', 'how'
}

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
        
        # Document frequency for each word (for TF-IDF)
        self.document_freq = defaultdict(int)
        self.total_documents = 0
        
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
            'text': 0.6,
            'subject': 0.2,  # Increased importance of subject
            'sender_domain': 0.2
        }
        
        # Feature importance tracking
        self.feature_importance = {
            'trash': defaultdict(float),
            'not_trash': defaultdict(float)
        }
        
        # Performance tracking
        self.training_time = 0.0
        self.evaluation_metrics = None
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text by converting to lowercase, removing non-alphanumeric chars,
        filtering stopwords and short words.
        
        Args:
            text: The text to preprocess
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        # Convert to lowercase
        text = text.lower()
        
        # Replace non-alphanumeric chars with spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split on whitespace
        tokens = text.split()
        
        # Filter short words and stopwords
        tokens = [word for word in tokens 
                 if len(word) >= self.min_word_length 
                 and word not in STOPWORDS]
        
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
        
        # Extract subject separately for weighting
        subject = email_data.get('subject', '')
        features['subject_tokens'] = self.preprocess_text(subject)
        
        # Get content/snippet features
        snippet = email_data.get('snippet', '')
        features['content_tokens'] = self.preprocess_text(snippet)
        
        # Combined tokens for general processing
        features['tokens'] = features['subject_tokens'] + features['content_tokens']
        
        # Get sender domain and email parts
        from_email = email_data.get('from_email', '')
        _, sender_address = parseaddr(from_email)
        
        features['sender_domain'] = ''
        features['sender_local_part'] = ''
        
        if '@' in sender_address:
            local_part, domain = sender_address.split('@', 1)
            features['sender_domain'] = domain.lower()
            features['sender_local_part'] = local_part.lower()
            
            # Check for common marketing/no-reply patterns
            if any(pattern in local_part.lower() for pattern in 
                  ['noreply', 'no-reply', 'donotreply', 'do-not-reply', 'marketing', 'newsletter', 
                   'news', 'updates', 'info', 'hello', 'support', 'team', 'notification']):
                features['sender_type'] = 'marketing'
            else:
                features['sender_type'] = 'personal'
        
        # Metadata features - time of day, etc.
        received_at = email_data.get('received_at')
        if received_at and isinstance(received_at, datetime):
            features['hour_received'] = received_at.hour
            features['is_weekend'] = 1 if received_at.weekday() >= 5 else 0
            features['is_business_hours'] = 1 if 9 <= received_at.hour <= 17 else 0
        
        return features
    
    def calculate_tfidf(self, token_counts: Dict[str, int], class_name: str) -> Dict[str, float]:
        """
        Calculate TF-IDF weights for tokens.
        
        Args:
            token_counts: Dictionary of token frequencies
            class_name: Class name ('trash' or 'not_trash')
            
        Returns:
            Dictionary of TF-IDF weights
        """
        if self.total_documents == 0:
            return {token: 1.0 for token in token_counts}
            
        # Calculate TF-IDF
        tfidf_weights = {}
        for token, count in token_counts.items():
            # Term frequency in this document
            tf = count / max(sum(token_counts.values()), 1)
            
            # Inverse document frequency
            idf = math.log(self.total_documents / max(self.document_freq.get(token, 1), 1))
            
            # TF-IDF
            tfidf_weights[token] = tf * idf
            
            # Track feature importance
            self.feature_importance[class_name][token] = tfidf_weights[token]
            
        return tfidf_weights
    
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
        self.document_freq = defaultdict(int)
        self.total_documents = 0
        self.sender_domain_counts = {'trash': defaultdict(int), 'not_trash': defaultdict(int)}
        self.sender_domain_totals = {'trash': 0, 'not_trash': 0}
        self.feature_importance = {'trash': defaultdict(float), 'not_trash': defaultdict(float)}
        
        # Get trash emails
        trash_query = db.query(Email).filter(Email.labels.contains(['TRASH']))
        if user_id:
            trash_query = trash_query.filter(Email.user_id == user_id)
        trash_emails = trash_query.all()
        
        # Get non-trash emails (from INBOX without TRASH label)
        non_trash_query = db.query(Email).filter(
            Email.labels.contains(['INBOX']),
            ~Email.labels.contains(['TRASH'])
        )
        if user_id:
            non_trash_query = non_trash_query.filter(Email.user_id == user_id)
        non_trash_emails = non_trash_query.order_by(Email.received_at.desc()).limit(len(trash_emails) * 2).all()
        
        logger.info(f"Training on {len(trash_emails)} trash emails and {len(non_trash_emails)} non-trash emails")
        
        # First pass: count document frequencies for all words
        all_emails = trash_emails + non_trash_emails
        self.total_documents = len(all_emails)
        
        for email in all_emails:
            email_data = {
                'subject': email.subject,
                'snippet': email.snippet,
                'from_email': email.from_email
            }
            
            features = self.extract_features(email_data)
            unique_tokens = set(features['tokens'])
            
            # Update document frequency for each unique token
            for token in unique_tokens:
                self.document_freq[token] += 1
        
        # Process trash emails
        word_freq_trash = Counter()
        subject_word_freq_trash = Counter()
        email_token_counts_trash = []  # Store token counts for each email for TF-IDF
        
        for email in trash_emails:
            self.class_priors['trash'] += 1
            
            email_data = {
                'subject': email.subject,
                'snippet': email.snippet,
                'from_email': email.from_email,
                'received_at': email.received_at
            }
            
            features = self.extract_features(email_data)
            
            # Count total tokens
            all_tokens = features['tokens']
            token_counts = Counter(all_tokens)
            email_token_counts_trash.append(token_counts)
            word_freq_trash.update(all_tokens)
            self.word_counts['trash'] += len(all_tokens)
            
            # Count subject tokens separately
            subject_tokens = features['subject_tokens']
            subject_word_freq_trash.update(subject_tokens)
            
            # Count sender domains
            sender_domain = features['sender_domain']
            if sender_domain:
                self.sender_domain_counts['trash'][sender_domain] += 1
                self.sender_domain_totals['trash'] += 1
        
        # Process non-trash emails
        word_freq_not_trash = Counter()
        subject_word_freq_not_trash = Counter()
        email_token_counts_not_trash = []
        
        for email in non_trash_emails:
            self.class_priors['not_trash'] += 1
            
            email_data = {
                'subject': email.subject,
                'snippet': email.snippet,
                'from_email': email.from_email,
                'received_at': email.received_at
            }
            
            features = self.extract_features(email_data)
            
            # Count all tokens
            all_tokens = features['tokens']
            token_counts = Counter(all_tokens)
            email_token_counts_not_trash.append(token_counts)
            word_freq_not_trash.update(all_tokens)
            self.word_counts['not_trash'] += len(all_tokens)
            
            # Count subject tokens separately
            subject_tokens = features['subject_tokens']
            subject_word_freq_not_trash.update(subject_tokens)
            
            # Count sender domains
            sender_domain = features['sender_domain']
            if sender_domain:
                self.sender_domain_counts['not_trash'][sender_domain] += 1
                self.sender_domain_totals['not_trash'] += 1
        
        # Calculate class priors
        total_emails = self.class_priors['trash'] + self.class_priors['not_trash']
        self.class_priors['trash'] /= total_emails
        self.class_priors['not_trash'] /= total_emails
        
        # Remove infrequent words and build vocabulary
        for word, count in list(word_freq_trash.items()):
            if count >= self.min_word_frequency:
                self.vocabulary.add(word)
        
        for word, count in list(word_freq_not_trash.items()):
            if count >= self.min_word_frequency:
                self.vocabulary.add(word)
        
        # Calculate average TF-IDF for each token in each class
        avg_tfidf_trash = defaultdict(float)
        for token_counts in email_token_counts_trash:
            tfidf_weights = self.calculate_tfidf(token_counts, 'trash')
            for token, weight in tfidf_weights.items():
                if token in self.vocabulary:
                    avg_tfidf_trash[token] += weight
        
        avg_tfidf_not_trash = defaultdict(float)
        for token_counts in email_token_counts_not_trash:
            tfidf_weights = self.calculate_tfidf(token_counts, 'not_trash')
            for token, weight in tfidf_weights.items():
                if token in self.vocabulary:
                    avg_tfidf_not_trash[token] += weight
        
        # Normalize by number of documents
        for token in self.vocabulary:
            if len(email_token_counts_trash) > 0:
                avg_tfidf_trash[token] /= len(email_token_counts_trash)
            if len(email_token_counts_not_trash) > 0:
                avg_tfidf_not_trash[token] /= len(email_token_counts_not_trash)
        
        # Calculate word likelihoods with Laplace smoothing and TF-IDF weighting
        vocab_size = len(self.vocabulary)
        alpha = self.laplace_smoothing_alpha
        
        for word in self.vocabulary:
            # Apply TF-IDF weighting
            tfidf_weight_trash = avg_tfidf_trash[word]
            tfidf_weight_not_trash = avg_tfidf_not_trash[word]
            
            # Combine word frequency with TF-IDF weight
            weighted_count_trash = word_freq_trash[word] * (1 + tfidf_weight_trash)
            weighted_count_not_trash = word_freq_not_trash[word] * (1 + tfidf_weight_not_trash)
            
            # P(word|trash) with Laplace smoothing and TF-IDF weighting
            self.word_likelihoods['trash'][word] = (weighted_count_trash + alpha) / (self.word_counts['trash'] + alpha * vocab_size)
            
            # P(word|not_trash) with Laplace smoothing and TF-IDF weighting
            self.word_likelihoods['not_trash'][word] = (weighted_count_not_trash + alpha) / (self.word_counts['not_trash'] + alpha * vocab_size)
            
            # Track feature importance based on class discrimination
            trash_likelihood = self.word_likelihoods['trash'][word]
            not_trash_likelihood = self.word_likelihoods['not_trash'][word]
            discrimination_power = abs(trash_likelihood - not_trash_likelihood)
            
            if trash_likelihood > not_trash_likelihood:
                self.feature_importance['trash'][word] = discrimination_power
            else:
                self.feature_importance['not_trash'][word] = discrimination_power
            
        # Apply special handling for subject words
        for word in set(subject_word_freq_trash) | set(subject_word_freq_not_trash):
            if word in self.vocabulary:
                # Increase the weight of subject words by 50%
                self.word_likelihoods['trash'][word] *= 1.5
                self.word_likelihoods['not_trash'][word] *= 1.5
        
        self.is_trained = True
        self.training_data_size = total_emails
        
        # Log most important features for each class
        top_trash_features = sorted(self.feature_importance['trash'].items(), key=lambda x: x[1], reverse=True)[:20]
        top_not_trash_features = sorted(self.feature_importance['not_trash'].items(), key=lambda x: x[1], reverse=True)[:20]
        
        logger.info(f"Top TRASH features: {', '.join([f'{word}:{score:.4f}' for word, score in top_trash_features])}")
        logger.info(f"Top NOT_TRASH features: {', '.join([f'{word}:{score:.4f}' for word, score in top_not_trash_features])}")
        
        training_results = {
            'vocabulary_size': vocab_size,
            'trash_emails': len(trash_emails),
            'non_trash_emails': len(non_trash_emails),
            'total_emails': total_emails,
            'trash_prior': self.class_priors['trash'],
            'not_trash_prior': self.class_priors['not_trash'],
            'top_trash_features': dict(top_trash_features),
            'top_not_trash_features': dict(top_not_trash_features)
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
            
            # Process content tokens with normal weight
            for token in features['content_tokens']:
                if token in self.vocabulary:
                    log_prob_trash += math.log(self.word_likelihoods['trash'][token]) * self.feature_weights['text']
                    log_prob_not_trash += math.log(self.word_likelihoods['not_trash'][token]) * self.feature_weights['text']
            
            # Process subject tokens with higher weight
            for token in features['subject_tokens']:
                if token in self.vocabulary:
                    log_prob_trash += math.log(self.word_likelihoods['trash'][token]) * self.feature_weights['subject']
                    log_prob_not_trash += math.log(self.word_likelihoods['not_trash'][token]) * self.feature_weights['subject']
            
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
            final_log_prob_trash = log_prob_trash + self.feature_weights['sender_domain'] * log_domain_prob_trash
            final_log_prob_not_trash = log_prob_not_trash + self.feature_weights['sender_domain'] * log_domain_prob_not_trash
            
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
                
            # Collect the features that contributed most to this classification
            if predicted_class == 'trash':
                contributing_features = [
                    f"subject_word:{token}" for token in features['subject_tokens'] 
                    if token in self.vocabulary and self.feature_importance['trash'].get(token, 0) > 0
                ][:3]
                contributing_features.extend([
                    f"content_word:{token}" for token in features['content_tokens'] 
                    if token in self.vocabulary and self.feature_importance['trash'].get(token, 0) > 0
                ][:3])
                if sender_domain and domain_prob_trash > 0.6:
                    contributing_features.append(f"sender:{sender_domain}")
            else:
                contributing_features = [
                    f"subject_word:{token}" for token in features['subject_tokens'] 
                    if token in self.vocabulary and self.feature_importance['not_trash'].get(token, 0) > 0
                ][:3]
                contributing_features.extend([
                    f"content_word:{token}" for token in features['content_tokens'] 
                    if token in self.vocabulary and self.feature_importance['not_trash'].get(token, 0) > 0
                ][:3])
                if sender_domain and domain_prob_not_trash > 0.6:
                    contributing_features.append(f"sender:{sender_domain}")
                
            # Attach contributing features to email_data for logging
            email_data['contributing_features'] = contributing_features
            
            return (predicted_class, confidence)
        except Exception as e:
            logger.error(f"[ML-CLASSIFIER] Classification error: {str(e)}", exc_info=True)
            return ('not_trash', 0.5)  # Default to not trash on error
    
    def save_model(self, filepath: str) -> None:
        """
        Save the trained model to disk
        
        Args:
            filepath: Path where the model should be saved
        """
        model_data = {
            'class_priors': self.class_priors,
            'word_likelihoods': dict(self.word_likelihoods),
            'word_counts': self.word_counts,
            'vocabulary': self.vocabulary,
            'sender_domain_counts': dict(self.sender_domain_counts),
            'sender_domain_totals': self.sender_domain_totals,
            'is_trained': self.is_trained,
            'training_data_size': self.training_data_size,
            'laplace_smoothing_alpha': self.laplace_smoothing_alpha,
            'min_word_length': self.min_word_length,
            'min_word_frequency': self.min_word_frequency,
            'feature_weights': self.feature_weights,
            'training_time': self.training_time,
            'evaluation_metrics': self.evaluation_metrics,
            'document_freq': dict(self.document_freq),
            'total_documents': self.total_documents,
            'feature_importance': dict(self.feature_importance)
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """
        Load a trained model from disk
        
        Args:
            filepath: Path to the saved model
        """
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.class_priors = model_data['class_priors']
        self.word_likelihoods = {
            'trash': defaultdict(float, model_data['word_likelihoods']['trash']),
            'not_trash': defaultdict(float, model_data['word_likelihoods']['not_trash'])
        }
        self.word_counts = model_data['word_counts']
        self.vocabulary = model_data['vocabulary']
        self.sender_domain_counts = {
            'trash': defaultdict(int, model_data['sender_domain_counts']['trash']),
            'not_trash': defaultdict(int, model_data['sender_domain_counts']['not_trash'])
        }
        self.sender_domain_totals = model_data['sender_domain_totals']
        self.is_trained = model_data['is_trained']
        self.training_data_size = model_data['training_data_size']
        
        # Load optional fields with defaults
        self.laplace_smoothing_alpha = model_data.get('laplace_smoothing_alpha', 1.0)
        self.min_word_length = model_data.get('min_word_length', 3)
        self.min_word_frequency = model_data.get('min_word_frequency', 2)
        self.feature_weights = model_data.get('feature_weights', {'text': 0.6, 'subject': 0.2, 'sender_domain': 0.2})
        self.training_time = model_data.get('training_time', 0.0)
        self.evaluation_metrics = model_data.get('evaluation_metrics', None)
        self.document_freq = defaultdict(int, model_data['document_freq'])
        self.total_documents = model_data['total_documents']
        self.feature_importance = defaultdict(float, model_data['feature_importance'])
        
        logger.info(f"Model loaded from {filepath} with vocabulary size: {len(self.vocabulary)}")

# Create a global instance for convenience
classifier = NaiveBayesClassifier()

def train_classifier(features: List[Dict[str, Any]], labels: List[int], user_id: Optional[UUID] = None) -> float:
    """
    Train the Naive Bayes classifier on the provided features and labels
    
    Args:
        features: List of feature dictionaries (sender, subject, snippet)
        labels: List of labels (1 for trash, 0 for not trash)
        user_id: Optional user ID for user-specific models
        
    Returns:
        Accuracy score on the training data
    """
    import time
    start_time = time.time()
    
    # Access global classifier
    global classifier
    
    # Initialize vocabulary and counts
    vocabulary = set()
    word_counts = {'trash': Counter(), 'not_trash': Counter()}
    class_counts = {'trash': 0, 'not_trash': 0}
    sender_domain_counts = {'trash': Counter(), 'not_trash': Counter()}
    
    # Count occurrences of each word in each class
    for i, (feature, label) in enumerate(zip(features, labels)):
        # Convert label to class name
        class_name = 'trash' if label == 1 else 'not_trash'
        class_counts[class_name] += 1
        
        # Process text features (subject and snippet)
        for field in ['subject', 'snippet']:
            if field in feature and feature[field]:
                tokens = classifier.preprocess_text(feature[field])
                for token in tokens:
                    word_counts[class_name][token] += 1
                    vocabulary.add(token)
        
        # Process sender domain
        if 'sender' in feature and feature['sender']:
            sender = feature['sender']
            domain = extract_domain(sender)
            if domain:
                sender_domain_counts[class_name][domain] += 1
    
    # Calculate class priors
    total_samples = len(labels)
    classifier.class_priors = {
        'trash': class_counts['trash'] / total_samples if total_samples > 0 else 0.5,
        'not_trash': class_counts['not_trash'] / total_samples if total_samples > 0 else 0.5
    }
    
    # Filter vocabulary by frequency
    min_frequency = classifier.min_word_frequency
    filtered_vocabulary = {word for word in vocabulary 
                          if word_counts['trash'][word] + word_counts['not_trash'][word] >= min_frequency}
    
    # Calculate word likelihoods with Laplace smoothing
    alpha = classifier.laplace_smoothing_alpha
    vocab_size = len(filtered_vocabulary)
    
    word_likelihoods = {
        'trash': {},
        'not_trash': {}
    }
    
    for word in filtered_vocabulary:
        # Calculate P(word|class) for each class with Laplace smoothing
        for class_name in ['trash', 'not_trash']:
            word_count = word_counts[class_name][word]
            total_words = sum(word_counts[class_name].values())
            
            # Laplace smoothing: (count + alpha) / (total + alpha * |V|)
            likelihood = (word_count + alpha) / (total_words + alpha * vocab_size)
            word_likelihoods[class_name][word] = likelihood
    
    # Update classifier with trained model
    classifier.vocabulary = filtered_vocabulary
    classifier.word_likelihoods = {
        'trash': defaultdict(float, word_likelihoods['trash']),
        'not_trash': defaultdict(float, word_likelihoods['not_trash'])
    }
    classifier.word_counts = {
        'trash': sum(word_counts['trash'].values()),
        'not_trash': sum(word_counts['not_trash'].values())
    }
    classifier.sender_domain_counts = {
        'trash': defaultdict(int, sender_domain_counts['trash']),
        'not_trash': defaultdict(int, sender_domain_counts['not_trash'])
    }
    classifier.sender_domain_totals = {
        'trash': sum(sender_domain_counts['trash'].values()),
        'not_trash': sum(sender_domain_counts['not_trash'].values())
    }
    classifier.is_trained = True
    classifier.training_data_size = total_samples
    
    # Track training time
    training_time = time.time() - start_time
    classifier.training_time = training_time
    
    # Calculate accuracy on training data
    correct = 0
    for i, (feature, label) in enumerate(zip(features, labels)):
        # Create email_data dict as expected by classify_email
        email_data = {
            "from_email": feature.get('sender', ''),
            "subject": feature.get('subject', ''),
            "snippet": feature.get('snippet', ''),
            "gmail_id": feature.get('gmail_id', 'unknown')
        }
        
        # Call the classifier with the expected parameter format
        prediction, _ = classify_email(email_data, user_id)
        
        if (prediction == 'trash' and label == 1) or (prediction == 'not_trash' and label == 0):
            correct += 1
    
    accuracy = correct / total_samples if total_samples > 0 else 0
    
    logger.info(f"Naive Bayes classifier trained on {total_samples} examples "
               f"({class_counts['trash']} trash, {class_counts['not_trash']} not trash) "
               f"with {len(filtered_vocabulary)} features in {training_time:.2f}s")
    
    return accuracy

def classify_email(email_data: Dict[str, Any], user_id: Optional[UUID] = None) -> Tuple[str, float]:
    """
    Convenience function to classify an email using the global or user-specific classifier.
    Ensures the right model is loaded for the current user.
    
    Args:
        email_data: Dictionary containing email data
        user_id: Optional UUID of the user for loading user-specific model
        
    Returns:
        Tuple of (predicted_class, confidence_score)
    """
    try:
        gmail_id = email_data.get('gmail_id', 'unknown')
        subject = email_data.get('subject', 'No subject')[:30]
        from_email = email_data.get('from_email', 'unknown')
        
        logger.info(f"[ML-CLASSIFIER] Classifying email: ID={gmail_id}, Subject='{subject}...', From={from_email}")
        
        # Check if we need to reload the model
        user_id_key = str(user_id) if user_id else 'global'
        now = datetime.now(timezone.utc)
        
        if user_id_key not in _model_load_time or (now - _model_load_time[user_id_key]).total_seconds() > _MODEL_CACHE_TTL:
            # Import here to avoid circular imports
            from ..services.email_classifier_service import load_trash_classifier
            
            # Load the appropriate model for this user
            if user_id:
                logger.debug(f"[ML-CLASSIFIER] Loading user-specific model for user {user_id}")
                model_loaded = load_trash_classifier(user_id)
                if not model_loaded:
                    logger.warning(f"[ML-CLASSIFIER] Failed to load user-specific model for {user_id}, defaulting to global model")
                    load_trash_classifier(None)  # Fall back to global model
            else:
                # Use global model
                logger.debug(f"[ML-CLASSIFIER] No user_id provided, using global model")
                load_trash_classifier(None)
                
            # Update cache time
            _model_load_time[user_id_key] = now
        else:
            logger.debug(f"[ML-CLASSIFIER] Using cached model for {user_id_key}")
        
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

def save_classifier_model(user_id: Optional[UUID] = None) -> str:
    """
    Convenience function to save the classifier model to disk
    
    Args:
        user_id: Optional UUID of the user for saving user-specific model
        
    Returns:
        Path to the saved model file
    """
    # Avoid circular import
    import os
    from pathlib import Path
    
    # Get the backend directory path
    backend_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    # Models directory is one level up from backend
    models_dir = backend_dir.parent / "models"
    
    # Determine file path based on user_id
    if user_id:
        filepath = str(models_dir / f"trash_classifier_{user_id}.pkl")
    else:
        filepath = str(models_dir / "trash_classifier_global.pkl")
    
    # Save the model
    classifier.save_model(filepath)
    logger.info(f"[ML-CLASSIFIER] Saved model to {filepath}")
    
    return filepath 

def load_classifier_model(user_id: Optional[UUID] = None) -> bool:
    """
    Convenience function to load the classifier model from disk
    
    Args:
        user_id: Optional UUID of the user for loading user-specific model
        
    Returns:
        Boolean indicating whether the model was loaded successfully
    """
    # Avoid circular import
    import os
    from pathlib import Path
    
    # Get the backend directory path
    backend_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    # Models directory is one level up from backend
    models_dir = backend_dir.parent / "models"
    
    # Determine file path based on user_id
    if user_id:
        user_model_path = models_dir / f"trash_classifier_{user_id}.pkl"
        global_model_path = models_dir / "trash_classifier_global.pkl"
        
        # Try user model first, then global model as fallback
        if user_model_path.exists():
            filepath = str(user_model_path)
            logger.debug(f"[ML-CLASSIFIER] Loading user-specific model from {filepath}")
        elif global_model_path.exists():
            filepath = str(global_model_path)
            logger.debug(f"[ML-CLASSIFIER] User model not found, falling back to global model: {filepath}")
        else:
            logger.warning(f"[ML-CLASSIFIER] No model found for user {user_id} or global")
            return False
    else:
        # Global model path
        global_model_path = models_dir / "trash_classifier_global.pkl"
        if global_model_path.exists():
            filepath = str(global_model_path)
            logger.debug(f"[ML-CLASSIFIER] Loading global model from {filepath}")
        else:
            logger.warning(f"[ML-CLASSIFIER] No global model found")
            return False
    
    try:
        # Load the model
        classifier.load_model(filepath)
        logger.info(f"[ML-CLASSIFIER] Successfully loaded model from {filepath}")
        return True
    except Exception as e:
        logger.error(f"[ML-CLASSIFIER] Error loading model from {filepath}: {str(e)}")
        return False 