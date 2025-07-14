/**
 * Attention scoring utilities for frontend
 * 
 * These functions mirror the backend attention scoring logic
 * to provide consistent attention level and color mapping.
 */

export function get_attention_level(score: number): string {
  /**
   * Convert attention score to human-readable level.
   * 
   * @param score - Attention score (0.0-100.0)
   * @returns Attention level ('Low', 'Medium', 'High', 'Critical')
   */
  if (score >= 80.0) {
    return 'Critical';
  } else if (score >= 60.0) {
    return 'High';
  } else if (score >= 30.0) {
    return 'Medium';
  } else {
    return 'Low';
  }
}

export function get_attention_color(score: number): string {
  /**
   * Get color representation for attention score (useful for UI).
   * 
   * @param score - Attention score (0.0-100.0)
   * @returns Color name ('red', 'orange', 'yellow', 'green')
   */
  if (score >= 80.0) {
    return 'red';
  } else if (score >= 60.0) {
    return 'orange';
  } else if (score >= 30.0) {
    return 'yellow';
  } else {
    return 'green';
  }
}

export function calculate_attention_score_from_data(
  is_read: boolean = false,
  labels: string[] = []
): number {
  /**
   * Calculate attention score from raw data (mirrors backend logic).
   * 
   * @param is_read - Whether the email has been read
   * @param labels - List of email labels
   * @returns Attention score between 0.0 and 100.0
   */
  let score = 50.0; // base score
  
  // Unread emails get higher attention
  if (!is_read) {
    score += 15.0;
  }
  
  // Check for urgency labels
  if (labels) {
    if (labels.includes('IMPORTANT')) {
      score += 30.0;
    }
    if (labels.includes('STARRED')) {
      score += 20.0;
    }
  }
  
  // Clamp result between 0.0 and 100.0
  return Math.max(0.0, Math.min(100.0, score));
} 