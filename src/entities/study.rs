use std::collections::HashSet;
use std::fs::File;
use std::io::BufRead;
use std::path::Path;

use crate::error::BioMcpError;

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct StudyInfo {
    pub study_id: String,
    pub name: String,
    pub cancer_type: Option<String>,
    pub citation: Option<String>,
    pub sample_count: Option<usize>,
    pub available_data: Vec<String>,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
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

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
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

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
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

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
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

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct CoOccurrenceResult {
    pub study_id: String,
    pub genes: Vec<String>,
    pub total_samples: usize,
    pub sample_universe_basis: SampleUniverseBasis,
    pub pairs: Vec<CoOccurrencePair>,
}

#[derive(Debug, Clone, Copy, serde::Serialize, serde::Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum SampleUniverseBasis {
    ClinicalSampleFile,
    MutationObserved,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
#[serde(tag = "query_type", content = "result", rename_all = "snake_case")]
pub enum StudyQueryResult {
    MutationFrequency(MutationFrequencyResult),
    CnaDistribution(CnaDistributionResult),
    ExpressionDistribution(ExpressionDistributionResult),
}

#[derive(Debug, Clone, Copy)]
pub enum StudyQueryType {
    Mutations,
    Cna,
    Expression,
}

impl StudyQueryType {
    pub fn from_flag(value: &str) -> Result<Self, BioMcpError> {
        match value.trim().to_ascii_lowercase().as_str() {
            "mutations" | "mutation" => Ok(Self::Mutations),
            "cna" | "copy_number" | "copy-number" => Ok(Self::Cna),
            "expression" | "expr" => Ok(Self::Expression),
            other => Err(BioMcpError::InvalidArgument(format!(
                "Unknown study query type '{other}'. Expected: mutations, cna, expression."
            ))),
        }
    }
}

pub async fn list_studies() -> Result<Vec<StudyInfo>, BioMcpError> {
    let root = crate::sources::cbioportal_study::resolve_study_root();
    run_blocking(move || {
        let studies = crate::sources::cbioportal_study::list_studies(&root)?;
        let mut out = Vec::with_capacity(studies.len());
        for study in studies {
            let mut available_data = Vec::new();
            if study.has_mutations {
                available_data.push("mutations".to_string());
            }
            if study.has_cna {
                available_data.push("cna".to_string());
            }
            if study.has_expression {
                available_data.push("expression".to_string());
            }
            if study.has_clinical_sample {
                available_data.push("clinical".to_string());
            }

            out.push(StudyInfo {
                study_id: study.study_id,
                name: study.meta.name,
                cancer_type: study.meta.cancer_type,
                citation: study.meta.citation,
                sample_count: clinical_sample_count(&study.path),
                available_data,
            });
        }
        Ok(out)
    })
    .await
}

pub async fn query_study(
    study_id: &str,
    gene: &str,
    query_type: StudyQueryType,
) -> Result<StudyQueryResult, BioMcpError> {
    let study_id = normalize_study_id(study_id)?;
    let gene = normalize_gene(gene)?;
    let root = crate::sources::cbioportal_study::resolve_study_root();

    run_blocking(move || {
        let study_dir = resolve_study_dir(&root, &study_id)?;
        match query_type {
            StudyQueryType::Mutations => Ok(StudyQueryResult::MutationFrequency(
                crate::sources::cbioportal_study::mutation_frequency(&study_dir, &gene)?.into(),
            )),
            StudyQueryType::Cna => Ok(StudyQueryResult::CnaDistribution(
                crate::sources::cbioportal_study::cna_distribution(&study_dir, &gene)?.into(),
            )),
            StudyQueryType::Expression => Ok(StudyQueryResult::ExpressionDistribution(
                crate::sources::cbioportal_study::expression_distribution(&study_dir, &gene)?
                    .into(),
            )),
        }
    })
    .await
}

pub async fn co_occurrence(
    study_id: &str,
    genes: &[String],
) -> Result<CoOccurrenceResult, BioMcpError> {
    let study_id = normalize_study_id(study_id)?;
    let genes = normalize_gene_list(genes)?;
    if genes.len() < 2 || genes.len() > 10 {
        return Err(BioMcpError::InvalidArgument(
            "Study co-occurrence requires 2 to 10 unique genes.".to_string(),
        ));
    }

    let root = crate::sources::cbioportal_study::resolve_study_root();
    run_blocking(move || {
        let study_dir = resolve_study_dir(&root, &study_id)?;
        let result = crate::sources::cbioportal_study::co_occurrence(&study_dir, &genes)?;
        Ok(result.into())
    })
    .await
}

impl From<crate::sources::cbioportal_study::MutationFrequencyResult> for MutationFrequencyResult {
    fn from(value: crate::sources::cbioportal_study::MutationFrequencyResult) -> Self {
        Self {
            study_id: value.study_id,
            gene: value.gene,
            mutation_count: value.mutation_count,
            unique_samples: value.unique_samples,
            total_samples: value.total_samples,
            frequency: value.frequency,
            top_variant_classes: value.top_variant_classes,
            top_protein_changes: value.top_protein_changes,
        }
    }
}

impl From<crate::sources::cbioportal_study::CnaDistributionResult> for CnaDistributionResult {
    fn from(value: crate::sources::cbioportal_study::CnaDistributionResult) -> Self {
        Self {
            study_id: value.study_id,
            gene: value.gene,
            total_samples: value.total_samples,
            deep_deletion: value.deep_deletion,
            shallow_deletion: value.shallow_deletion,
            diploid: value.diploid,
            gain: value.gain,
            amplification: value.amplification,
        }
    }
}

impl From<crate::sources::cbioportal_study::ExpressionDistributionResult>
    for ExpressionDistributionResult
{
    fn from(value: crate::sources::cbioportal_study::ExpressionDistributionResult) -> Self {
        Self {
            study_id: value.study_id,
            gene: value.gene,
            file: value.file,
            sample_count: value.sample_count,
            mean: value.mean,
            median: value.median,
            min: value.min,
            max: value.max,
            q1: value.q1,
            q3: value.q3,
        }
    }
}

impl From<crate::sources::cbioportal_study::CoOccurrencePair> for CoOccurrencePair {
    fn from(value: crate::sources::cbioportal_study::CoOccurrencePair) -> Self {
        Self {
            gene_a: value.gene_a,
            gene_b: value.gene_b,
            both_mutated: value.both_mutated,
            a_only: value.a_only,
            b_only: value.b_only,
            neither: value.neither,
            log_odds_ratio: value.log_odds_ratio,
            p_value: value.p_value,
        }
    }
}

impl From<crate::sources::cbioportal_study::CoOccurrenceResult> for CoOccurrenceResult {
    fn from(value: crate::sources::cbioportal_study::CoOccurrenceResult) -> Self {
        Self {
            study_id: value.study_id,
            genes: value.genes,
            total_samples: value.total_samples,
            sample_universe_basis: value.sample_universe_basis.into(),
            pairs: value.pairs.into_iter().map(Into::into).collect(),
        }
    }
}

impl From<crate::sources::cbioportal_study::SampleUniverseBasis> for SampleUniverseBasis {
    fn from(value: crate::sources::cbioportal_study::SampleUniverseBasis) -> Self {
        match value {
            crate::sources::cbioportal_study::SampleUniverseBasis::ClinicalSampleFile => {
                Self::ClinicalSampleFile
            }
            crate::sources::cbioportal_study::SampleUniverseBasis::MutationObserved => {
                Self::MutationObserved
            }
        }
    }
}

fn normalize_study_id(study_id: &str) -> Result<String, BioMcpError> {
    let study_id = study_id.trim();
    if study_id.is_empty() {
        return Err(BioMcpError::InvalidArgument(
            "Study ID is required.".to_string(),
        ));
    }
    Ok(study_id.to_string())
}

fn normalize_gene(gene: &str) -> Result<String, BioMcpError> {
    let gene = gene.trim();
    if gene.is_empty() {
        return Err(BioMcpError::InvalidArgument(
            "Gene is required.".to_string(),
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
    for gene in genes {
        let normalized = normalize_gene(gene)?;
        if seen.insert(normalized.clone()) {
            out.push(normalized);
        }
    }
    Ok(out)
}

fn resolve_study_dir(root: &Path, study_id: &str) -> Result<std::path::PathBuf, BioMcpError> {
    let studies = crate::sources::cbioportal_study::list_studies(root)?;
    studies
        .into_iter()
        .find(|study| study.study_id.eq_ignore_ascii_case(study_id))
        .map(|study| study.path)
        .ok_or_else(|| BioMcpError::NotFound {
            entity: "study".to_string(),
            id: study_id.to_string(),
            suggestion: "Try listing available studies: biomcp study list".to_string(),
        })
}

fn clinical_sample_count(study_dir: &Path) -> Option<usize> {
    let path = study_dir.join("data_clinical_sample.txt");
    let file = File::open(path).ok()?;
    let mut lines = std::io::BufReader::new(file).lines();

    let mut sample_idx = None;
    for next in lines.by_ref() {
        let line = next.ok()?;
        let trimmed = line.trim();
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }
        let header = line
            .split('\t')
            .map(|value| value.trim().to_ascii_uppercase())
            .collect::<Vec<_>>();
        sample_idx = header.iter().position(|col| col == "SAMPLE_ID");
        break;
    }

    let sample_idx = sample_idx?;
    let mut samples = HashSet::new();
    for next in lines {
        let line = next.ok()?;
        let trimmed = line.trim();
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }
        let fields = line.split('\t').collect::<Vec<_>>();
        let sample = fields.get(sample_idx).copied().unwrap_or("").trim();
        if !sample.is_empty() {
            samples.insert(sample.to_string());
        }
    }
    Some(samples.len())
}

async fn run_blocking<T, F>(work: F) -> Result<T, BioMcpError>
where
    T: Send + 'static,
    F: FnOnce() -> Result<T, BioMcpError> + Send + 'static,
{
    tokio::task::spawn_blocking(work)
        .await
        .map_err(|err| BioMcpError::Api {
            api: "study".to_string(),
            message: format!("Study query worker failed: {err}"),
        })?
}

#[cfg(test)]
mod tests {
    use super::*;

    use std::fs;
    use std::path::{Path, PathBuf};
    use std::sync::{Mutex, OnceLock};
    use std::time::{SystemTime, UNIX_EPOCH};

    fn env_lock() -> &'static Mutex<()> {
        static LOCK: OnceLock<Mutex<()>> = OnceLock::new();
        LOCK.get_or_init(|| Mutex::new(()))
    }

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
                "biomcp-study-entity-test-{name}-{}-{unique}",
                std::process::id()
            ));
            fs::create_dir_all(&root).expect("create root");
            Self { root }
        }
    }

    impl Drop for TestStudyDir {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.root);
        }
    }

    fn write_file(path: &Path, content: &str) {
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent).expect("create parent");
        }
        fs::write(path, content).expect("write file");
    }

    fn minimal_study_fixture(root: &Path, study_id: &str) {
        let study = root.join(study_id);
        fs::create_dir_all(&study).expect("create study");
        write_file(
            &study.join("meta_study.txt"),
            &format!(
                "cancer_study_identifier: {study_id}\nname: {study_id} name\ntype_of_cancer: mixed\ncitation: demo citation\n"
            ),
        );
        write_file(
            &study.join("data_mutations.txt"),
            "Hugo_Symbol\tTumor_Sample_Barcode\tVariant_Classification\tHGVSp_Short\nTP53\tS1\tMissense_Mutation\tp.R175H\nTP53\tS2\tMissense_Mutation\tp.R248Q\nKRAS\tS2\tMissense_Mutation\tp.G12D\n",
        );
        write_file(
            &study.join("data_clinical_sample.txt"),
            "# comment\nPATIENT_ID\tSAMPLE_ID\tCANCER_TYPE\tCANCER_TYPE_DETAILED\tONCOTREE_CODE\nP1\tS1\tLung Cancer\tLung Adenocarcinoma\tLUAD\nP2\tS2\tLung Cancer\tLung Adenocarcinoma\tLUAD\nP3\tS3\tLung Cancer\tLung Adenocarcinoma\tLUAD\n",
        );
        write_file(
            &study.join("data_cna.txt"),
            "Hugo_Symbol\tS1\tS2\tS3\nTP53\t-2\t0\t2\n",
        );
        write_file(
            &study.join("data_mrna_seq_v2_rsem_zscores_ref_all_samples.txt"),
            "Hugo_Symbol\tEntrez_Gene_Id\tS1\tS2\tS3\nTP53\t7157\t1.0\t2.0\t3.0\n",
        );
    }

    #[test]
    fn query_type_from_flag_parses_supported_values() {
        assert!(matches!(
            StudyQueryType::from_flag("mutations").expect("mutations should parse"),
            StudyQueryType::Mutations
        ));
        assert!(matches!(
            StudyQueryType::from_flag("cna").expect("cna should parse"),
            StudyQueryType::Cna
        ));
        assert!(matches!(
            StudyQueryType::from_flag("expression").expect("expression should parse"),
            StudyQueryType::Expression
        ));
    }

    #[test]
    fn query_type_from_flag_rejects_unknown_type() {
        let err = StudyQueryType::from_flag("foo").expect_err("unknown type should fail");
        assert!(matches!(err, BioMcpError::InvalidArgument(_)));
    }

    #[tokio::test]
    async fn list_studies_returns_available_data() {
        let _guard = env_lock()
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner());
        let fixture = TestStudyDir::new("list");
        minimal_study_fixture(&fixture.root, "demo_study");
        // SAFETY: tests serialize env var mutation through a process-wide mutex.
        unsafe {
            std::env::set_var("BIOMCP_STUDY_DIR", &fixture.root);
        }

        let studies = list_studies().await.expect("list studies");
        assert_eq!(studies.len(), 1);
        assert_eq!(studies[0].study_id, "demo_study");
        assert!(studies[0].available_data.contains(&"mutations".to_string()));
        assert!(studies[0].available_data.contains(&"cna".to_string()));
        assert!(
            studies[0]
                .available_data
                .contains(&"expression".to_string())
        );
        assert_eq!(studies[0].sample_count, Some(3));
    }

    #[tokio::test]
    async fn query_study_mutations_round_trips_source_result() {
        let _guard = env_lock()
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner());
        let fixture = TestStudyDir::new("query-mutations");
        minimal_study_fixture(&fixture.root, "demo_study");
        // SAFETY: tests serialize env var mutation through a process-wide mutex.
        unsafe {
            std::env::set_var("BIOMCP_STUDY_DIR", &fixture.root);
        }

        let result = query_study("demo_study", "TP53", StudyQueryType::Mutations)
            .await
            .expect("query should pass");
        match result {
            StudyQueryResult::MutationFrequency(result) => {
                assert_eq!(result.study_id, "demo_study");
                assert_eq!(result.gene, "TP53");
                assert_eq!(result.mutation_count, 2);
                assert_eq!(result.unique_samples, 2);
                assert_eq!(result.total_samples, 3);
            }
            other => panic!("unexpected query result: {other:?}"),
        }
    }

    #[tokio::test]
    async fn query_study_unknown_study_returns_not_found() {
        let _guard = env_lock()
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner());
        let fixture = TestStudyDir::new("unknown-study");
        minimal_study_fixture(&fixture.root, "demo_study");
        // SAFETY: tests serialize env var mutation through a process-wide mutex.
        unsafe {
            std::env::set_var("BIOMCP_STUDY_DIR", &fixture.root);
        }

        let err = query_study("missing", "TP53", StudyQueryType::Mutations)
            .await
            .expect_err("unknown study should fail");
        assert!(matches!(err, BioMcpError::NotFound { .. }));
    }

    #[tokio::test]
    async fn co_occurrence_validates_gene_count() {
        let _guard = env_lock()
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner());
        let fixture = TestStudyDir::new("co-occur-count");
        minimal_study_fixture(&fixture.root, "demo_study");
        // SAFETY: tests serialize env var mutation through a process-wide mutex.
        unsafe {
            std::env::set_var("BIOMCP_STUDY_DIR", &fixture.root);
        }

        let err = co_occurrence("demo_study", &["TP53".to_string()])
            .await
            .expect_err("one gene should fail");
        assert!(matches!(err, BioMcpError::InvalidArgument(_)));
    }
}
