//! Pure Rust prefilter logic (CPF-shaped, email, Luhn-valid card sequences).
//! Used by the PyO3 `FastFilter` wrapper and by unit tests without a Python runtime.

use regex::Regex;

/// Compiled regex set built once per `FastFilter` instance.
pub struct CompiledPatterns {
    cpf_pattern: Regex,
    email_pattern: Regex,
    credit_card_pattern: Regex,
}

impl CompiledPatterns {
    /// Build the same patterns as `FastFilter::new` in `lib.rs`.
    pub fn new() -> Result<Self, regex::Error> {
        let cpf_pattern = Regex::new(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}")?;
        let email_pattern = Regex::new(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")?;
        let credit_card_pattern = Regex::new(r"\b(?:\d[ -]*?){13,19}\b")?;
        Ok(Self {
            cpf_pattern,
            email_pattern,
            credit_card_pattern,
        })
    }

    /// Return indexes of rows that look like PII (CPF-shaped, email, or Luhn-valid card run).
    pub fn suspect_indices(&self, batch: &[String]) -> Vec<usize> {
        let mut suspects = Vec::new();
        for (idx, content) in batch.iter().enumerate() {
            if self.cpf_pattern.is_match(content) || self.email_pattern.is_match(content) {
                suspects.push(idx);
                continue;
            }
            if self.has_valid_luhn_card(content) {
                suspects.push(idx);
            }
        }
        suspects
    }

    fn has_valid_luhn_card(&self, content: &str) -> bool {
        self.credit_card_pattern
            .find_iter(content)
            .any(|m| check_luhn(m.as_str()))
    }
}

/// Luhn check on digit runs; ignores spaces and hyphens in `card_number`.
//
// `% 2` / `% 10` keep the canonical Luhn arithmetic readable. The
// `clippy::manual_is_multiple_of` lint (clippy 1.95+) suggests
// `.is_multiple_of(...)` but that std method only stabilized in Rust 1.87 for
// unsigned ints, which would break older toolColleague-Nns used by contributors and
// the lab. We choose readable + portable over chasing the newest clippy hint.
#[allow(unknown_lints, clippy::manual_is_multiple_of)]
pub fn check_luhn(card_number: &str) -> bool {
    let digits: Vec<u32> = card_number
        .chars()
        .filter(|c| c.is_ascii_digit())
        .filter_map(|c| c.to_digit(10))
        .collect();

    if digits.len() < 13 || digits.len() > 19 {
        return false;
    }

    let sum: u32 = digits
        .iter()
        .rev()
        .enumerate()
        .map(|(i, &digit)| {
            if i % 2 == 1 {
                let d = digit * 2;
                if d > 9 { d - 9 } else { d }
            } else {
                digit
            }
        })
        .sum();

    sum % 10 == 0
}

#[cfg(test)]
mod tests {
    use super::*;

    fn patterns() -> CompiledPatterns {
        CompiledPatterns::new().expect("test regexes compile")
    }

    #[test]
    fn luhn_valid_visa_test_pattern() {
        assert!(check_luhn("4111111111111111"));
        assert!(check_luhn("4111 1111 1111 1111"));
    }

    #[test]
    fn luhn_invalid_single_digit_flip() {
        assert!(!check_luhn("4111111111111112"));
    }

    #[test]
    fn luhn_rejects_too_short() {
        assert!(!check_luhn("411111111111"));
    }

    #[test]
    fn luhn_rejects_too_long() {
        let s = "4".repeat(20);
        assert!(!check_luhn(&s));
    }

    #[test]
    fn suspect_indices_cpf_dotted_masked_email_and_valid_card() {
        let p = patterns();
        let batch = vec![
            "123.456.789-00".to_string(),
            "texto comum".to_string(),
            "contato@empresa.com".to_string(),
            "cartao valido 4111 1111 1111 1111".to_string(),
            "cartao invalido 4111 1111 1111 1112".to_string(),
        ];
        let idx = p.suspect_indices(&batch);
        assert_eq!(idx, vec![0, 2, 3]);
    }

    #[test]
    fn suspect_indices_plain_digits_cpf_shape() {
        let p = patterns();
        let batch = vec!["12345678900".to_string()];
        assert_eq!(p.suspect_indices(&batch), vec![0]);
    }

    #[test]
    fn suspect_indices_no_match_innocuous_text() {
        let p = patterns();
        let batch = vec!["hello world no pii".to_string()];
        assert!(p.suspect_indices(&batch).is_empty());
    }
}
