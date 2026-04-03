#![allow(dead_code)]

use std::borrow::Cow;

use reqwest_middleware::ClientWithMiddleware;
use serde::Deserialize;

use crate::error::BioMcpError;

const PUBMED_EUTILS_BASE: &str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils";
const PUBMED_EUTILS_BASE_ENV: &str = "BIOMCP_PUBMED_BASE";
const PUBMED_EUTILS_API: &str = "pubmed-eutils";

#[derive(Clone)]
pub struct PubMedClient {
    client: ClientWithMiddleware,
    base: Cow<'static, str>,
    api_key: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) struct PubMedESearchParams {
    pub term: String,
    pub retstart: usize,
    pub retmax: usize,
    pub date_from: Option<String>,
    pub date_to: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) struct PubMedESearchResponse {
    pub count: u64,
    pub idlist: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct ESearchEnvelope {
    esearchresult: ESearchInner,
}

#[derive(Debug, Deserialize)]
struct ESearchInner {
    count: String,
    #[serde(default)]
    idlist: Vec<String>,
}

fn format_pubmed_date(value: &str) -> String {
    value.trim().replace('-', "/")
}

impl PubMedClient {
    pub fn new() -> Result<Self, BioMcpError> {
        Ok(Self {
            client: crate::sources::shared_client()?,
            base: crate::sources::env_base(PUBMED_EUTILS_BASE, PUBMED_EUTILS_BASE_ENV),
            api_key: crate::sources::ncbi_api_key(),
        })
    }

    #[cfg(test)]
    fn new_for_test(base: String, api_key: Option<String>) -> Result<Self, BioMcpError> {
        Ok(Self {
            client: Self::test_client()?,
            base: Cow::Owned(base),
            api_key: api_key
                .map(|value| value.trim().to_string())
                .filter(|value| !value.is_empty()),
        })
    }

    #[cfg(test)]
    fn test_client() -> Result<ClientWithMiddleware, BioMcpError> {
        let base = reqwest::Client::builder()
            .timeout(std::time::Duration::from_secs(10))
            .connect_timeout(std::time::Duration::from_secs(5))
            .user_agent(concat!("biomcp-cli-test/", env!("CARGO_PKG_VERSION")))
            .build()
            .map_err(BioMcpError::HttpClientInit)?;
        Ok(reqwest_middleware::ClientBuilder::new(base).build())
    }

    fn endpoint(&self, path: &str) -> String {
        format!(
            "{}/{}",
            self.base.as_ref().trim_end_matches('/'),
            path.trim_start_matches('/')
        )
    }

    async fn get_json<T: serde::de::DeserializeOwned>(
        &self,
        req: reqwest_middleware::RequestBuilder,
    ) -> Result<T, BioMcpError> {
        let resp = crate::sources::apply_cache_mode_with_auth(req, self.api_key.is_some())
            .send()
            .await?;
        let status = resp.status();
        let content_type = resp.headers().get(reqwest::header::CONTENT_TYPE).cloned();
        let bytes = crate::sources::read_limited_body(resp, PUBMED_EUTILS_API).await?;
        if !status.is_success() {
            let excerpt = crate::sources::body_excerpt(&bytes);
            return Err(BioMcpError::Api {
                api: PUBMED_EUTILS_API.to_string(),
                message: format!("HTTP {status}: {excerpt}"),
            });
        }
        crate::sources::ensure_json_content_type(PUBMED_EUTILS_API, content_type.as_ref(), &bytes)?;
        serde_json::from_slice(&bytes).map_err(|source| BioMcpError::ApiJson {
            api: PUBMED_EUTILS_API.to_string(),
            source,
        })
    }

    pub async fn esearch(
        &self,
        params: &PubMedESearchParams,
    ) -> Result<PubMedESearchResponse, BioMcpError> {
        let term = params.term.trim();
        if term.is_empty() {
            return Err(BioMcpError::InvalidArgument(
                "PubMed ESearch term is required".into(),
            ));
        }
        if term.len() > 4096 {
            return Err(BioMcpError::InvalidArgument(
                "PubMed ESearch term is too long".into(),
            ));
        }
        if params.retmax == 0 || params.retmax > 10_000 {
            return Err(BioMcpError::InvalidArgument(
                "PubMed ESearch retmax must be between 1 and 10000".into(),
            ));
        }

        let url = self.endpoint("esearch.fcgi");
        let retstart = params.retstart.to_string();
        let retmax = params.retmax.to_string();
        let mut req = self.client.get(&url).query(&[
            ("db", "pubmed"),
            ("retmode", "json"),
            ("term", term),
            ("retstart", retstart.as_str()),
            ("retmax", retmax.as_str()),
        ]);

        if params.date_from.is_some() || params.date_to.is_some() {
            req = req.query(&[("datetype", "pdat")]);
        }
        if let Some(date_from) = params
            .date_from
            .as_deref()
            .map(str::trim)
            .filter(|value| !value.is_empty())
        {
            let mindate = format_pubmed_date(date_from);
            req = req.query(&[("mindate", mindate.as_str())]);
        }
        if let Some(date_to) = params
            .date_to
            .as_deref()
            .map(str::trim)
            .filter(|value| !value.is_empty())
        {
            let maxdate = format_pubmed_date(date_to);
            req = req.query(&[("maxdate", maxdate.as_str())]);
        }

        let req = crate::sources::append_ncbi_api_key(req, self.api_key.as_deref());
        let response: ESearchEnvelope = self.get_json(req).await?;
        let count = response
            .esearchresult
            .count
            .trim()
            .parse::<u64>()
            .map_err(|_| BioMcpError::Api {
                api: PUBMED_EUTILS_API.to_string(),
                message: format!(
                    "Invalid ESearch count value {:?} from upstream contract",
                    response.esearchresult.count
                ),
            })?;

        Ok(PubMedESearchResponse {
            count,
            idlist: response.esearchresult.idlist,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use wiremock::matchers::{method, path, query_param};
    use wiremock::{Mock, MockServer, ResponseTemplate};

    #[tokio::test]
    async fn esearch_sets_required_query_params() {
        let server = MockServer::start().await;
        Mock::given(method("GET"))
            .and(path("/esearch.fcgi"))
            .and(query_param("db", "pubmed"))
            .and(query_param("retmode", "json"))
            .and(query_param("term", "BRAF melanoma"))
            .and(query_param("retstart", "5"))
            .and(query_param("retmax", "20"))
            .respond_with(ResponseTemplate::new(200).set_body_json(serde_json::json!({
                "esearchresult": {
                    "count": "2",
                    "idlist": ["123", "456"]
                }
            })))
            .expect(1)
            .mount(&server)
            .await;

        let client = PubMedClient::new_for_test(server.uri(), None).expect("client");
        let response = client
            .esearch(&PubMedESearchParams {
                term: "BRAF melanoma".into(),
                retstart: 5,
                retmax: 20,
                date_from: None,
                date_to: None,
            })
            .await
            .expect("esearch should succeed");

        assert_eq!(response.count, 2);
        assert_eq!(response.idlist, vec!["123".to_string(), "456".to_string()]);
    }

    #[tokio::test]
    async fn esearch_appends_ncbi_api_key() {
        let server = MockServer::start().await;
        Mock::given(method("GET"))
            .and(path("/esearch.fcgi"))
            .and(query_param("db", "pubmed"))
            .and(query_param("term", "BRAF"))
            .and(query_param("retstart", "0"))
            .and(query_param("retmax", "10"))
            .and(query_param("retmode", "json"))
            .and(query_param("api_key", "test-key"))
            .respond_with(ResponseTemplate::new(200).set_body_json(serde_json::json!({
                "esearchresult": {
                    "count": "0",
                    "idlist": []
                }
            })))
            .expect(1)
            .mount(&server)
            .await;

        let client =
            PubMedClient::new_for_test(server.uri(), Some("test-key".into())).expect("client");
        let response = client
            .esearch(&PubMedESearchParams {
                term: "BRAF".into(),
                retstart: 0,
                retmax: 10,
                date_from: None,
                date_to: None,
            })
            .await
            .expect("esearch should succeed");

        assert_eq!(response.count, 0);
        assert!(response.idlist.is_empty());
    }

    #[tokio::test]
    async fn esearch_applies_date_range_params() {
        let server = MockServer::start().await;
        Mock::given(method("GET"))
            .and(path("/esearch.fcgi"))
            .and(query_param("db", "pubmed"))
            .and(query_param("term", "BRAF"))
            .and(query_param("retstart", "0"))
            .and(query_param("retmax", "10"))
            .and(query_param("retmode", "json"))
            .and(query_param("datetype", "pdat"))
            .and(query_param("mindate", "2020/01/01"))
            .and(query_param("maxdate", "2024/12/31"))
            .respond_with(ResponseTemplate::new(200).set_body_json(serde_json::json!({
                "esearchresult": {
                    "count": "1",
                    "idlist": ["31832001"]
                }
            })))
            .expect(1)
            .mount(&server)
            .await;

        let client = PubMedClient::new_for_test(server.uri(), None).expect("client");
        let response = client
            .esearch(&PubMedESearchParams {
                term: "BRAF".into(),
                retstart: 0,
                retmax: 10,
                date_from: Some("2020-01-01".into()),
                date_to: Some("2024-12-31".into()),
            })
            .await
            .expect("esearch should succeed");

        assert_eq!(response.idlist, vec!["31832001".to_string()]);
    }

    #[tokio::test]
    async fn esearch_handles_empty_idlist() {
        let server = MockServer::start().await;
        Mock::given(method("GET"))
            .and(path("/esearch.fcgi"))
            .and(query_param("db", "pubmed"))
            .and(query_param("term", "BRAF"))
            .and(query_param("retstart", "0"))
            .and(query_param("retmax", "5"))
            .and(query_param("retmode", "json"))
            .respond_with(ResponseTemplate::new(200).set_body_json(serde_json::json!({
                "esearchresult": {
                    "count": "0",
                    "idlist": []
                }
            })))
            .expect(1)
            .mount(&server)
            .await;

        let client = PubMedClient::new_for_test(server.uri(), None).expect("client");
        let response = client
            .esearch(&PubMedESearchParams {
                term: "BRAF".into(),
                retstart: 0,
                retmax: 5,
                date_from: None,
                date_to: None,
            })
            .await
            .expect("esearch should succeed");

        assert_eq!(response.count, 0);
        assert!(response.idlist.is_empty());
    }

    #[tokio::test]
    async fn esearch_surfaces_http_error_context() {
        let server = MockServer::start().await;
        Mock::given(method("GET"))
            .and(path("/esearch.fcgi"))
            .respond_with(ResponseTemplate::new(500).set_body_string("upstream failure"))
            .expect(1)
            .mount(&server)
            .await;

        let client = PubMedClient::new_for_test(server.uri(), None).expect("client");
        let err = client
            .esearch(&PubMedESearchParams {
                term: "BRAF".into(),
                retstart: 0,
                retmax: 5,
                date_from: None,
                date_to: None,
            })
            .await
            .expect_err("http failure should surface");

        let msg = err.to_string();
        assert!(msg.contains("pubmed-eutils"));
        assert!(msg.contains("500"));
    }

    #[tokio::test]
    async fn esearch_rejects_non_numeric_count() {
        let server = MockServer::start().await;
        Mock::given(method("GET"))
            .and(path("/esearch.fcgi"))
            .and(query_param("db", "pubmed"))
            .and(query_param("term", "BRAF"))
            .and(query_param("retstart", "0"))
            .and(query_param("retmax", "5"))
            .and(query_param("retmode", "json"))
            .respond_with(ResponseTemplate::new(200).set_body_json(serde_json::json!({
                "esearchresult": {
                    "count": "not-a-number",
                    "idlist": ["123"]
                }
            })))
            .expect(1)
            .mount(&server)
            .await;

        let client = PubMedClient::new_for_test(server.uri(), None).expect("client");
        let err = client
            .esearch(&PubMedESearchParams {
                term: "BRAF".into(),
                retstart: 0,
                retmax: 5,
                date_from: None,
                date_to: None,
            })
            .await
            .expect_err("non-numeric count should fail");

        let msg = err.to_string();
        assert!(msg.contains("pubmed-eutils"));
        assert!(msg.contains("count"));
    }

    #[tokio::test]
    async fn esearch_rejects_empty_term() {
        let client = PubMedClient::new_for_test("http://127.0.0.1".into(), None).expect("client");
        let err = client
            .esearch(&PubMedESearchParams {
                term: "   ".into(),
                retstart: 0,
                retmax: 5,
                date_from: None,
                date_to: None,
            })
            .await
            .expect_err("empty term should fail");

        assert!(matches!(err, BioMcpError::InvalidArgument(_)));
        assert!(err.to_string().contains("term"));
    }
}
