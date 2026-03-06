use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::{BufRead, BufReader, Lines};
use std::path::{Path, PathBuf};

use crate::error::BioMcpError;

const SOURCE_NAME: &str = "cbioportal-study";
const META_STUDY_FILE: &str = "meta_study.txt";
const MUTATIONS_FILE: &str = "data_mutations.txt";
const CLINICAL_SAMPLE_FILE: &str = "data_clinical_sample.txt";
const CNA_FILE: &str = "data_cna.txt";
const EXPRESSION_FILES: &[&str] = &[
    "data_mrna_seq_v2_rsem_zscores_ref_all_samples.txt",
    "data_mrna_seq_v2_rsem.txt",
];

#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct StudyMeta {
    pub study_id: String,
    pub name: String,
    pub short_name: Option<String>,
    pub description: Option<String>,
    pub cancer_type: Option<String>,
    pub citation: Option<String>,
    pub pmid: Option<String>,
}

#[derive(Debug, Clone)]
pub struct StudyDataset {
    pub study_id: String,
    pub path: PathBuf,
    pub meta: StudyMeta,
    pub has_mutations: bool,
    pub has_cna: bool,
    pub has_expression: bool,
    pub has_clinical_sample: bool,
}

#[derive(Debug, Clone)]
pub struct MutationFrequencyResult {
    pub study_id: String,
    pub gene: String,
    pub mutation_count: usize,
    pub unique_samples: usize,
    pub total_samples: usize,
    pub frequency: f64,
    pub top_variant_classes: Vec<(String, usize)>,
    pub top_protein_changes: Vec<(String, usize)>,
}

#[derive(Debug, Clone)]
pub struct CnaDistributionResult {
    pub study_id: String,
    pub gene: String,
    pub total_samples: usize,
    pub deep_deletion: usize,
    pub shallow_deletion: usize,
    pub diploid: usize,
    pub gain: usize,
    pub amplification: usize,
}

#[derive(Debug, Clone)]
pub struct ExpressionDistributionResult {
    pub study_id: String,
    pub gene: String,
    pub file: String,
    pub sample_count: usize,
    pub mean: f64,
    pub median: f64,
    pub min: f64,
    pub max: f64,
    pub q1: f64,
    pub q3: f64,
}

#[derive(Debug, Clone)]
pub struct CoOccurrencePair {
    pub gene_a: String,
    pub gene_b: String,
    pub both_mutated: usize,
    pub a_only: usize,
    pub b_only: usize,
    pub neither: usize,
    pub log_odds_ratio: Option<f64>,
    pub p_value: Option<f64>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SampleUniverseBasis {
    ClinicalSampleFile,
    MutationObserved,
}

#[derive(Debug, Clone)]
pub struct CoOccurrenceResult {
    pub study_id: String,
    pub genes: Vec<String>,
    pub total_samples: usize,
    pub sample_universe_basis: SampleUniverseBasis,
    pub pairs: Vec<CoOccurrencePair>,
}

pub fn resolve_study_root() -> PathBuf {
    if let Some(path) = std::env::var("BIOMCP_STUDY_DIR")
        .ok()
        .map(|v| v.trim().to_string())
        .filter(|v| !v.is_empty())
    {
        return PathBuf::from(path);
    }

    match dirs::data_dir() {
        Some(path) => path.join("biomcp").join("studies"),
        None => std::env::temp_dir().join("biomcp").join("studies"),
    }
}

pub fn list_studies(root: &Path) -> Result<Vec<StudyDataset>, BioMcpError> {
    if !root.exists() {
        return Err(BioMcpError::SourceUnavailable {
            source_name: SOURCE_NAME.to_string(),
            reason: format!("Study root does not exist: {}", root.display()),
            suggestion: "Set BIOMCP_STUDY_DIR to a directory containing study folders.".to_string(),
        });
    }

    if !root.is_dir() {
        return Err(BioMcpError::SourceUnavailable {
            source_name: SOURCE_NAME.to_string(),
            reason: format!("Study root is not a directory: {}", root.display()),
            suggestion: "Set BIOMCP_STUDY_DIR to a directory containing study folders.".to_string(),
        });
    }

    let mut studies = Vec::new();
    for entry in std::fs::read_dir(root)? {
        let entry = entry?;
        let path = entry.path();
        if !path.is_dir() {
            continue;
        }

        let dir_study_id = path
            .file_name()
            .and_then(|s| s.to_str())
            .map(str::trim)
            .filter(|s| !s.is_empty())
            .unwrap_or("unknown")
            .to_string();

        let meta_path = path.join(META_STUDY_FILE);
        let meta = if meta_path.exists() {
            parse_meta_study(&meta_path, &dir_study_id)?
        } else {
            StudyMeta {
                study_id: dir_study_id.clone(),
                name: dir_study_id.clone(),
                short_name: None,
                description: None,
                cancer_type: None,
                citation: None,
                pmid: None,
            }
        };

        studies.push(StudyDataset {
            study_id: meta.study_id.clone(),
            path: path.clone(),
            meta,
            has_mutations: path.join(MUTATIONS_FILE).exists(),
            has_cna: path.join(CNA_FILE).exists(),
            has_expression: find_expression_file(&path).is_some(),
            has_clinical_sample: path.join(CLINICAL_SAMPLE_FILE).exists(),
        });
    }

    studies.sort_by(|a, b| a.study_id.cmp(&b.study_id));
    Ok(studies)
}

pub fn mutation_frequency(
    study_dir: &Path,
    gene: &str,
) -> Result<MutationFrequencyResult, BioMcpError> {
    let gene = normalize_gene(gene)?;
    let study_id = study_id_from_dir(study_dir);

    let path = study_dir.join(MUTATIONS_FILE);
    let mut reader = TsvReader::open(&path)?;
    let header = header_map(&reader.headers);

    let gene_idx = require_column(&header, "HUGO_SYMBOL", &path)?;
    let sample_idx = column_index(&header, &["TUMOR_SAMPLE_BARCODE", "SAMPLE_ID"]);
    let variant_class_idx = column_index(&header, &["VARIANT_CLASSIFICATION"]);
    let protein_change_idx = column_index(&header, &["HGVSP_SHORT", "AMINO_ACID_CHANGE"]);

    let mut mutation_count = 0usize;
    let mut unique_samples = HashSet::new();
    let mut variant_counts: HashMap<String, usize> = HashMap::new();
    let mut protein_counts: HashMap<String, usize> = HashMap::new();

    while let Some(row) = reader.next_row()? {
        if !row_field(&row, gene_idx).eq_ignore_ascii_case(&gene) {
            continue;
        }

        mutation_count += 1;

        if let Some(idx) = sample_idx {
            let sample = row_field(&row, idx);
            if !sample.is_empty() {
                unique_samples.insert(sample.to_string());
            }
        }

        if let Some(idx) = variant_class_idx {
            let value = row_field(&row, idx);
            let class_name = if value.is_empty() {
                "unknown".to_string()
            } else {
                value.to_string()
            };
            *variant_counts.entry(class_name).or_insert(0) += 1;
        }

        if let Some(idx) = protein_change_idx {
            let value = row_field(&row, idx);
            if !value.is_empty() {
                *protein_counts.entry(value.to_string()).or_insert(0) += 1;
            }
        }
    }

    let total_samples = clinical_sample_ids(study_dir)?
        .map(|ids| ids.len())
        .filter(|count| *count > 0)
        .unwrap_or(unique_samples.len());
    let frequency = if total_samples > 0 {
        unique_samples.len() as f64 / total_samples as f64
    } else {
        0.0
    };

    Ok(MutationFrequencyResult {
        study_id,
        gene,
        mutation_count,
        unique_samples: unique_samples.len(),
        total_samples,
        frequency,
        top_variant_classes: sorted_counts(variant_counts),
        top_protein_changes: sorted_counts(protein_counts),
    })
}

pub fn cna_distribution(
    study_dir: &Path,
    gene: &str,
) -> Result<CnaDistributionResult, BioMcpError> {
    let gene = normalize_gene(gene)?;
    let study_id = study_id_from_dir(study_dir);

    let path = study_dir.join(CNA_FILE);
    let mut reader = TsvReader::open(&path)?;
    let header = header_map(&reader.headers);
    let gene_idx = require_column(&header, "HUGO_SYMBOL", &path)?;
    let sample_start = matrix_sample_start(&header, &reader.headers, &path)?;

    while let Some(row) = reader.next_row()? {
        if !row_field(&row, gene_idx).eq_ignore_ascii_case(&gene) {
            continue;
        }

        let mut deep_deletion = 0usize;
        let mut shallow_deletion = 0usize;
        let mut diploid = 0usize;
        let mut gain = 0usize;
        let mut amplification = 0usize;

        for value in row.iter().skip(sample_start) {
            let Some(v) = parse_i32(value) else { continue };
            match v {
                -2 => deep_deletion += 1,
                -1 => shallow_deletion += 1,
                0 => diploid += 1,
                1 => gain += 1,
                2 => amplification += 1,
                _ => {}
            }
        }

        let total_samples = deep_deletion + shallow_deletion + diploid + gain + amplification;
        return Ok(CnaDistributionResult {
            study_id,
            gene,
            total_samples,
            deep_deletion,
            shallow_deletion,
            diploid,
            gain,
            amplification,
        });
    }

    Err(BioMcpError::NotFound {
        entity: "gene".to_string(),
        id: gene,
        suggestion: format!("Try a different gene symbol in study '{study_id}'."),
    })
}

pub fn expression_distribution(
    study_dir: &Path,
    gene: &str,
) -> Result<ExpressionDistributionResult, BioMcpError> {
    let gene = normalize_gene(gene)?;
    let study_id = study_id_from_dir(study_dir);

    let path = find_expression_file(study_dir).ok_or_else(|| BioMcpError::SourceUnavailable {
        source_name: SOURCE_NAME.to_string(),
        reason: format!(
            "No supported expression matrix found under {}",
            study_dir.display()
        ),
        suggestion: "Use a study with expression data or query type mutations/cna.".to_string(),
    })?;

    let mut reader = TsvReader::open(&path)?;
    let header = header_map(&reader.headers);
    let gene_idx = require_column(&header, "HUGO_SYMBOL", &path)?;
    let sample_start = matrix_sample_start(&header, &reader.headers, &path)?;

    while let Some(row) = reader.next_row()? {
        if !row_field(&row, gene_idx).eq_ignore_ascii_case(&gene) {
            continue;
        }

        let mut values = row
            .iter()
            .skip(sample_start)
            .filter_map(|v| parse_f64(v))
            .collect::<Vec<_>>();
        values.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));

        if values.is_empty() {
            return Ok(ExpressionDistributionResult {
                study_id,
                gene,
                file: path
                    .file_name()
                    .and_then(|s| s.to_str())
                    .unwrap_or_default()
                    .to_string(),
                sample_count: 0,
                mean: 0.0,
                median: 0.0,
                min: 0.0,
                max: 0.0,
                q1: 0.0,
                q3: 0.0,
            });
        }

        let sample_count = values.len();
        let sum: f64 = values.iter().sum();
        let mean = sum / sample_count as f64;
        let median = quantile_inclusive(&values, 0.5);
        let q1 = quantile_inclusive(&values, 0.25);
        let q3 = quantile_inclusive(&values, 0.75);

        return Ok(ExpressionDistributionResult {
            study_id,
            gene,
            file: path
                .file_name()
                .and_then(|s| s.to_str())
                .unwrap_or_default()
                .to_string(),
            sample_count,
            mean,
            median,
            min: *values.first().unwrap_or(&0.0),
            max: *values.last().unwrap_or(&0.0),
            q1,
            q3,
        });
    }

    Err(BioMcpError::NotFound {
        entity: "gene".to_string(),
        id: gene,
        suggestion: format!("Try a different gene symbol in study '{study_id}'."),
    })
}

pub fn co_occurrence(
    study_dir: &Path,
    genes: &[String],
) -> Result<CoOccurrenceResult, BioMcpError> {
    let genes = normalize_gene_list(genes)?;
    if genes.len() < 2 {
        return Err(BioMcpError::InvalidArgument(
            "Co-occurrence requires at least 2 genes.".to_string(),
        ));
    }

    let study_id = study_id_from_dir(study_dir);
    let path = study_dir.join(MUTATIONS_FILE);
    let mut reader = TsvReader::open(&path)?;
    let header = header_map(&reader.headers);

    let gene_idx = require_column(&header, "HUGO_SYMBOL", &path)?;
    let sample_idx =
        column_index(&header, &["TUMOR_SAMPLE_BARCODE", "SAMPLE_ID"]).ok_or_else(|| {
            BioMcpError::SourceUnavailable {
                source_name: SOURCE_NAME.to_string(),
                reason: format!(
                    "Missing SAMPLE_ID/Tumor_Sample_Barcode column in {}",
                    path.display()
                ),
                suggestion: "Use a valid cBioPortal mutation file.".to_string(),
            }
        })?;

    let requested: HashSet<String> = genes.iter().cloned().collect();
    let mut mutated_by_gene: HashMap<String, HashSet<String>> =
        genes.iter().map(|g| (g.clone(), HashSet::new())).collect();
    let mut observed_samples = HashSet::new();

    while let Some(row) = reader.next_row()? {
        let sample = row_field(&row, sample_idx);
        if sample.is_empty() {
            continue;
        }
        observed_samples.insert(sample.to_string());

        let row_gene = row_field(&row, gene_idx).to_ascii_uppercase();
        if !requested.contains(&row_gene) {
            continue;
        }
        if let Some(samples) = mutated_by_gene.get_mut(&row_gene) {
            samples.insert(sample.to_string());
        }
    }

    let (sample_universe, sample_universe_basis) = match clinical_sample_ids(study_dir)? {
        Some(ids) if !ids.is_empty() => (ids, SampleUniverseBasis::ClinicalSampleFile),
        _ => (observed_samples, SampleUniverseBasis::MutationObserved),
    };
    let total_samples = sample_universe.len();

    let mut pairs = Vec::new();
    for i in 0..genes.len() {
        for j in (i + 1)..genes.len() {
            let gene_a = &genes[i];
            let gene_b = &genes[j];
            let set_a = mutated_by_gene
                .get(gene_a)
                .expect("gene set initialized for co-occurrence");
            let set_b = mutated_by_gene
                .get(gene_b)
                .expect("gene set initialized for co-occurrence");

            let both_mutated = set_a
                .iter()
                .filter(|sample| sample_universe.contains(*sample) && set_b.contains(*sample))
                .count();
            let a_only = set_a
                .iter()
                .filter(|sample| sample_universe.contains(*sample) && !set_b.contains(*sample))
                .count();
            let b_only = set_b
                .iter()
                .filter(|sample| sample_universe.contains(*sample) && !set_a.contains(*sample))
                .count();
            let neither = total_samples.saturating_sub(both_mutated + a_only + b_only);

            pairs.push(CoOccurrencePair {
                gene_a: gene_a.clone(),
                gene_b: gene_b.clone(),
                both_mutated,
                a_only,
                b_only,
                neither,
                log_odds_ratio: log_odds_ratio(both_mutated, a_only, b_only, neither),
                p_value: None,
            });
        }
    }

    Ok(CoOccurrenceResult {
        study_id,
        genes,
        total_samples,
        sample_universe_basis,
        pairs,
    })
}

fn parse_meta_study(path: &Path, fallback_study_id: &str) -> Result<StudyMeta, BioMcpError> {
    let file = File::open(path).map_err(|_| BioMcpError::SourceUnavailable {
        source_name: SOURCE_NAME.to_string(),
        reason: format!("Missing study metadata file: {}", path.display()),
        suggestion: "Ensure each study folder contains meta_study.txt.".to_string(),
    })?;

    let mut study_id = fallback_study_id.to_string();
    let mut name = fallback_study_id.to_string();
    let mut short_name = None;
    let mut description = None;
    let mut cancer_type = None;
    let mut citation = None;
    let mut pmid = None;

    for line in BufReader::new(file).lines() {
        let line = line?;
        let trimmed = line.trim();
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }
        let Some((raw_key, raw_value)) = trimmed.split_once(':') else {
            continue;
        };
        let key = raw_key.trim().to_ascii_lowercase();
        let value = raw_value.trim();

        match key.as_str() {
            "cancer_study_identifier" => {
                if !value.is_empty() {
                    study_id = value.to_string();
                }
            }
            "name" => {
                if !value.is_empty() {
                    name = value.to_string();
                }
            }
            "short_name" => {
                short_name = non_empty(value);
            }
            "description" => {
                description = non_empty(value);
            }
            "type_of_cancer" => {
                cancer_type = non_empty(value);
            }
            "citation" => {
                citation = non_empty(value);
            }
            "pmid" => {
                pmid = non_empty(value);
            }
            _ => {}
        }
    }

    Ok(StudyMeta {
        study_id,
        name,
        short_name,
        description,
        cancer_type,
        citation,
        pmid,
    })
}

fn non_empty(value: &str) -> Option<String> {
    let trimmed = value.trim();
    (!trimmed.is_empty()).then(|| trimmed.to_string())
}

fn find_expression_file(study_dir: &Path) -> Option<PathBuf> {
    for name in EXPRESSION_FILES {
        let path = study_dir.join(name);
        if path.exists() {
            return Some(path);
        }
    }
    None
}

fn normalize_gene(gene: &str) -> Result<String, BioMcpError> {
    let gene = gene.trim();
    if gene.is_empty() {
        return Err(BioMcpError::InvalidArgument(
            "Gene is required for study query.".to_string(),
        ));
    }
    if !crate::sources::is_valid_gene_symbol(gene) {
        return Err(BioMcpError::InvalidArgument(format!(
            "Invalid gene symbol: {gene}"
        )));
    }
    Ok(gene.to_ascii_uppercase())
}

fn normalize_gene_list(genes: &[String]) -> Result<Vec<String>, BioMcpError> {
    let mut out = Vec::new();
    let mut seen = HashSet::new();
    for raw in genes {
        let gene = normalize_gene(raw)?;
        if seen.insert(gene.clone()) {
            out.push(gene);
        }
    }
    Ok(out)
}

fn study_id_from_dir(study_dir: &Path) -> String {
    study_dir
        .file_name()
        .and_then(|s| s.to_str())
        .map(str::trim)
        .filter(|v| !v.is_empty())
        .unwrap_or("unknown")
        .to_string()
}

fn parse_f64(value: &str) -> Option<f64> {
    let value = value.trim();
    if value.is_empty() || matches!(value.to_ascii_uppercase().as_str(), "NA" | "NAN" | "NULL") {
        return None;
    }
    value.parse::<f64>().ok()
}

fn parse_i32(value: &str) -> Option<i32> {
    let value = value.trim();
    if value.is_empty() || matches!(value.to_ascii_uppercase().as_str(), "NA" | "NAN" | "NULL") {
        return None;
    }
    value.parse::<i32>().ok()
}

fn sorted_counts(map: HashMap<String, usize>) -> Vec<(String, usize)> {
    let mut out = map.into_iter().collect::<Vec<_>>();
    out.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));
    out
}

fn quantile_inclusive(sorted: &[f64], p: f64) -> f64 {
    if sorted.is_empty() {
        return 0.0;
    }
    if sorted.len() == 1 {
        return sorted[0];
    }

    let position = p.clamp(0.0, 1.0) * (sorted.len() - 1) as f64;
    let lower = position.floor() as usize;
    let upper = position.ceil() as usize;
    if lower == upper {
        return sorted[lower];
    }
    let weight = position - lower as f64;
    sorted[lower] * (1.0 - weight) + sorted[upper] * weight
}

fn log_odds_ratio(both: usize, a_only: usize, b_only: usize, neither: usize) -> Option<f64> {
    let total = both + a_only + b_only + neither;
    if total == 0 {
        return None;
    }

    let mut a = both as f64;
    let mut b = a_only as f64;
    let mut c = b_only as f64;
    let mut d = neither as f64;
    if a == 0.0 || b == 0.0 || c == 0.0 || d == 0.0 {
        a += 0.5;
        b += 0.5;
        c += 0.5;
        d += 0.5;
    }

    Some(((a * d) / (b * c)).ln())
}

fn clinical_sample_ids(study_dir: &Path) -> Result<Option<HashSet<String>>, BioMcpError> {
    let path = study_dir.join(CLINICAL_SAMPLE_FILE);
    if !path.exists() {
        return Ok(None);
    }

    let mut reader = TsvReader::open(&path)?;
    let header = header_map(&reader.headers);
    let Some(sample_idx) = column_index(&header, &["SAMPLE_ID"]) else {
        return Ok(None);
    };

    let mut samples = HashSet::new();
    while let Some(row) = reader.next_row()? {
        let sample = row_field(&row, sample_idx);
        if !sample.is_empty() {
            samples.insert(sample.to_string());
        }
    }
    Ok(Some(samples))
}

fn matrix_sample_start(
    header: &HashMap<String, usize>,
    headers: &[String],
    path: &Path,
) -> Result<usize, BioMcpError> {
    let hugo_idx = require_column(header, "HUGO_SYMBOL", path)?;
    let sample_start = match header.get("ENTREZ_GENE_ID") {
        Some(entrez_idx) if *entrez_idx > hugo_idx => entrez_idx + 1,
        _ => hugo_idx + 1,
    };
    if sample_start >= headers.len() {
        return Err(BioMcpError::SourceUnavailable {
            source_name: SOURCE_NAME.to_string(),
            reason: format!("No sample columns found in {}", path.display()),
            suggestion: "Use a valid cBioPortal matrix file with sample columns.".to_string(),
        });
    }
    Ok(sample_start)
}

fn row_field(row: &[String], idx: usize) -> &str {
    row.get(idx).map(String::as_str).unwrap_or("").trim()
}

fn normalize_header(value: &str) -> String {
    value.trim_matches('\u{feff}').trim().to_ascii_uppercase()
}

fn header_map(headers: &[String]) -> HashMap<String, usize> {
    headers
        .iter()
        .enumerate()
        .map(|(idx, col)| (normalize_header(col), idx))
        .collect()
}

fn column_index(header: &HashMap<String, usize>, names: &[&str]) -> Option<usize> {
    names
        .iter()
        .find_map(|name| header.get(&normalize_header(name)).copied())
}

fn require_column(
    header: &HashMap<String, usize>,
    column: &str,
    path: &Path,
) -> Result<usize, BioMcpError> {
    header
        .get(&normalize_header(column))
        .copied()
        .ok_or_else(|| BioMcpError::SourceUnavailable {
            source_name: SOURCE_NAME.to_string(),
            reason: format!("Missing required column '{column}' in {}", path.display()),
            suggestion: "Use a valid cBioPortal data file for this study.".to_string(),
        })
}

struct TsvReader {
    headers: Vec<String>,
    lines: Lines<BufReader<File>>,
}

impl TsvReader {
    fn open(path: &Path) -> Result<Self, BioMcpError> {
        let file = File::open(path).map_err(|_| BioMcpError::SourceUnavailable {
            source_name: SOURCE_NAME.to_string(),
            reason: format!("Missing required file: {}", path.display()),
            suggestion: "Check BIOMCP_STUDY_DIR and dataset contents.".to_string(),
        })?;

        let mut lines = BufReader::new(file).lines();
        let mut header = None;
        for next in lines.by_ref() {
            let line = next?;
            let trimmed = line.trim();
            if trimmed.is_empty() || trimmed.starts_with('#') {
                continue;
            }
            header = Some(
                line.split('\t')
                    .map(|v| v.trim_end_matches('\r').to_string())
                    .collect::<Vec<_>>(),
            );
            break;
        }

        let headers = header.ok_or_else(|| BioMcpError::SourceUnavailable {
            source_name: SOURCE_NAME.to_string(),
            reason: format!("No header found in {}", path.display()),
            suggestion: "Use a valid non-empty TSV file.".to_string(),
        })?;

        Ok(Self { headers, lines })
    }

    fn next_row(&mut self) -> Result<Option<Vec<String>>, BioMcpError> {
        for next in self.lines.by_ref() {
            let line = next?;
            let trimmed = line.trim();
            if trimmed.is_empty() || trimmed.starts_with('#') {
                continue;
            }

            let mut row = line
                .split('\t')
                .map(|v| v.trim_end_matches('\r').to_string())
                .collect::<Vec<_>>();
            if row.len() < self.headers.len() {
                row.resize(self.headers.len(), String::new());
            }
            return Ok(Some(row));
        }
        Ok(None)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    use std::fs;
    use std::time::{SystemTime, UNIX_EPOCH};

    struct TestStudyDir {
        root: PathBuf,
    }

    impl TestStudyDir {
        fn new(name: &str) -> Self {
            let unique = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .expect("system clock before unix epoch")
                .as_nanos();
            let root = std::env::temp_dir().join(format!(
                "biomcp-study-source-test-{name}-{}-{unique}",
                std::process::id()
            ));
            fs::create_dir_all(&root).expect("create root");
            Self { root }
        }

        fn study_path(&self, study_id: &str) -> PathBuf {
            let path = self.root.join(study_id);
            fs::create_dir_all(&path).expect("create study dir");
            path
        }

        fn write_file(&self, path: &Path, content: &str) {
            if let Some(parent) = path.parent() {
                fs::create_dir_all(parent).expect("create parent");
            }
            fs::write(path, content).expect("write test file");
        }
    }

    impl Drop for TestStudyDir {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.root);
        }
    }

    fn write_minimal_clinical_samples(study_dir: &Path, rows: &[&str]) {
        let mut content = String::from(
            "# comment 1\n# comment 2\nPATIENT_ID\tSAMPLE_ID\tCANCER_TYPE\tCANCER_TYPE_DETAILED\tONCOTREE_CODE\n",
        );
        for row in rows {
            content.push_str(row);
            content.push('\n');
        }
        fs::write(study_dir.join("data_clinical_sample.txt"), content)
            .expect("write clinical sample");
    }

    #[test]
    fn list_studies_reads_meta_and_data_flags() {
        let fixture = TestStudyDir::new("list-studies");
        let study_dir = fixture.study_path("demo_study");
        fixture.write_file(
            &study_dir.join("meta_study.txt"),
            "cancer_study_identifier: demo_study\nname: Demo Study\nshort_name: Demo\ntype_of_cancer: mixed\ncitation: Demo et al.\npmid: 12345\n",
        );
        fixture.write_file(
            &study_dir.join("data_mutations.txt"),
            "Hugo_Symbol\tTumor_Sample_Barcode\tVariant_Classification\tHGVSp_Short\nTP53\tS1\tMissense_Mutation\tp.R175H\n",
        );
        fixture.write_file(
            &study_dir.join("data_cna.txt"),
            "Hugo_Symbol\tS1\nTP53\t1\n",
        );
        fixture.write_file(
            &study_dir.join("data_mrna_seq_v2_rsem_zscores_ref_all_samples.txt"),
            "Hugo_Symbol\tEntrez_Gene_Id\tS1\nTP53\t7157\t0.3\n",
        );
        write_minimal_clinical_samples(
            &study_dir,
            &["P1\tS1\tLung Cancer\tLung Adenocarcinoma\tLUAD"],
        );

        let studies = list_studies(&fixture.root).expect("list studies");
        assert_eq!(studies.len(), 1);
        let study = &studies[0];
        assert_eq!(study.study_id, "demo_study");
        assert_eq!(study.meta.name, "Demo Study");
        assert_eq!(study.meta.short_name.as_deref(), Some("Demo"));
        assert_eq!(study.meta.cancer_type.as_deref(), Some("mixed"));
        assert_eq!(study.meta.citation.as_deref(), Some("Demo et al."));
        assert_eq!(study.meta.pmid.as_deref(), Some("12345"));
        assert!(study.has_mutations);
        assert!(study.has_cna);
        assert!(study.has_expression);
        assert!(study.has_clinical_sample);
    }

    #[test]
    fn mutation_frequency_counts_records_samples_and_top_buckets() {
        let fixture = TestStudyDir::new("mutation-frequency");
        let study_dir = fixture.study_path("mf_study");
        fixture.write_file(
            &study_dir.join("data_mutations.txt"),
            "#metadata line\nHugo_Symbol\tTumor_Sample_Barcode\tVariant_Classification\tHGVSp_Short\nTP53\tS1\tMissense_Mutation\tp.R175H\nTP53\tS1\tNonsense_Mutation\tp.R196*\nTP53\tS2\tMissense_Mutation\tp.R248Q\nEGFR\tS3\tMissense_Mutation\tp.L858R\n",
        );
        write_minimal_clinical_samples(
            &study_dir,
            &[
                "P1\tS1\tLung Cancer\tLung Adenocarcinoma\tLUAD",
                "P2\tS2\tLung Cancer\tLung Squamous Cell Carcinoma\tLUSC",
                "P3\tS3\tLung Cancer\tLung Adenocarcinoma\tLUAD",
            ],
        );

        let result = mutation_frequency(&study_dir, "tp53").expect("mutation frequency");
        assert_eq!(result.study_id, "mf_study");
        assert_eq!(result.gene, "TP53");
        assert_eq!(result.mutation_count, 3);
        assert_eq!(result.unique_samples, 2);
        assert_eq!(result.total_samples, 3);
        assert!((result.frequency - (2.0 / 3.0)).abs() < 1e-9);
        assert_eq!(
            result.top_variant_classes,
            vec![
                ("Missense_Mutation".to_string(), 2),
                ("Nonsense_Mutation".to_string(), 1)
            ]
        );
        assert_eq!(
            result.top_protein_changes,
            vec![
                ("p.R175H".to_string(), 1),
                ("p.R196*".to_string(), 1),
                ("p.R248Q".to_string(), 1)
            ]
        );
    }

    #[test]
    fn cna_distribution_supports_header_with_entrez_column() {
        let fixture = TestStudyDir::new("cna-dist");
        let study_dir = fixture.study_path("cna_study");
        fixture.write_file(
            &study_dir.join("data_cna.txt"),
            "Hugo_Symbol\tEntrez_Gene_Id\tS1\tS2\tS3\tS4\tS5\nTP53\t7157\t-2\t-1\t0\t1\t2\n",
        );

        let result = cna_distribution(&study_dir, "TP53").expect("cna distribution");
        assert_eq!(result.study_id, "cna_study");
        assert_eq!(result.gene, "TP53");
        assert_eq!(result.total_samples, 5);
        assert_eq!(result.deep_deletion, 1);
        assert_eq!(result.shallow_deletion, 1);
        assert_eq!(result.diploid, 1);
        assert_eq!(result.gain, 1);
        assert_eq!(result.amplification, 1);
    }

    #[test]
    fn expression_distribution_ignores_na_and_empty_values() {
        let fixture = TestStudyDir::new("expr-dist");
        let study_dir = fixture.study_path("expr_study");
        fixture.write_file(
            &study_dir.join("data_mrna_seq_v2_rsem_zscores_ref_all_samples.txt"),
            "Hugo_Symbol\tEntrez_Gene_Id\tS1\tS2\tS3\tS4\tS5\nESR1\t2099\t1.0\tNA\t\t2.0\t3.0\n",
        );

        let result = expression_distribution(&study_dir, "ESR1").expect("expression distribution");
        assert_eq!(result.study_id, "expr_study");
        assert_eq!(result.gene, "ESR1");
        assert_eq!(
            result.file,
            "data_mrna_seq_v2_rsem_zscores_ref_all_samples.txt"
        );
        assert_eq!(result.sample_count, 3);
        assert!((result.mean - 2.0).abs() < 1e-9);
        assert!((result.median - 2.0).abs() < 1e-9);
        assert!((result.min - 1.0).abs() < 1e-9);
        assert!((result.max - 3.0).abs() < 1e-9);
        assert!((result.q1 - 1.5).abs() < 1e-9);
        assert!((result.q3 - 2.5).abs() < 1e-9);
    }

    #[test]
    fn co_occurrence_computes_pair_counts() {
        let fixture = TestStudyDir::new("co-occur");
        let study_dir = fixture.study_path("co_study");
        fixture.write_file(
            &study_dir.join("data_mutations.txt"),
            "Hugo_Symbol\tTumor_Sample_Barcode\tVariant_Classification\tHGVSp_Short\nTP53\tS1\tMissense_Mutation\tp.R175H\nKRAS\tS1\tMissense_Mutation\tp.G12D\nTP53\tS2\tMissense_Mutation\tp.R248Q\nKRAS\tS3\tMissense_Mutation\tp.G12V\nEGFR\tS4\tMissense_Mutation\tp.L858R\n",
        );
        write_minimal_clinical_samples(
            &study_dir,
            &[
                "P1\tS1\tLung Cancer\tLung Adenocarcinoma\tLUAD",
                "P2\tS2\tLung Cancer\tLung Adenocarcinoma\tLUAD",
                "P3\tS3\tLung Cancer\tLung Adenocarcinoma\tLUAD",
                "P4\tS4\tLung Cancer\tLung Adenocarcinoma\tLUAD",
                "P5\tS5\tLung Cancer\tLung Adenocarcinoma\tLUAD",
            ],
        );

        let result = co_occurrence(&study_dir, &["TP53".into(), "KRAS".into()])
            .expect("co-occurrence result");
        assert_eq!(result.study_id, "co_study");
        assert_eq!(result.total_samples, 5);
        assert_eq!(
            result.sample_universe_basis,
            SampleUniverseBasis::ClinicalSampleFile
        );
        assert_eq!(result.pairs.len(), 1);
        let pair = &result.pairs[0];
        assert_eq!(pair.gene_a, "TP53");
        assert_eq!(pair.gene_b, "KRAS");
        assert_eq!(pair.both_mutated, 1);
        assert_eq!(pair.a_only, 1);
        assert_eq!(pair.b_only, 1);
        assert_eq!(pair.neither, 2);
        assert!(pair.log_odds_ratio.is_some());
        assert!(pair.p_value.is_none());
    }

    #[test]
    fn co_occurrence_falls_back_to_mutation_observed_samples_without_clinical_file() {
        let fixture = TestStudyDir::new("co-occur-no-clinical");
        let study_dir = fixture.study_path("co_study");
        fixture.write_file(
            &study_dir.join("data_mutations.txt"),
            "Hugo_Symbol\tTumor_Sample_Barcode\tVariant_Classification\tHGVSp_Short\nTP53\tS1\tMissense_Mutation\tp.R175H\nTP53\tS2\tMissense_Mutation\tp.R248Q\nKRAS\tS2\tMissense_Mutation\tp.G12D\nKRAS\tS3\tMissense_Mutation\tp.G12V\n",
        );

        let result = co_occurrence(&study_dir, &["TP53".into(), "KRAS".into()])
            .expect("co-occurrence result");
        assert_eq!(result.total_samples, 3);
        assert_eq!(
            result.sample_universe_basis,
            SampleUniverseBasis::MutationObserved
        );
        let pair = &result.pairs[0];
        assert_eq!(pair.both_mutated, 1);
        assert_eq!(pair.a_only, 1);
        assert_eq!(pair.b_only, 1);
        assert_eq!(pair.neither, 0);
    }

    #[test]
    fn missing_required_file_returns_source_unavailable() {
        let fixture = TestStudyDir::new("missing-file");
        let study_dir = fixture.study_path("missing_study");
        let err = mutation_frequency(&study_dir, "TP53").expect_err("missing file should fail");
        assert!(matches!(err, BioMcpError::SourceUnavailable { .. }));
    }
}
