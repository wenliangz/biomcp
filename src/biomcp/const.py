#
# Default timeout for caching HTTP requests.
#
DEFAULT_CACHE_TIMEOUT = 60 * 60 * 24 * 7  # 1 week

#
# Currently limiting all searches to 40 results. We will want to make this
# more configurable by endpoint and overrideable by the calling application.
#
SYSTEM_PAGE_SIZE = 40

#
# Pubtator3 API
# https://www.ncbi.nlm.nih.gov/research/pubtator3/api
#
PUBTATOR3_BASE = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api"

#
# ClinicalTrials.gov API
# https://clinicaltrials.gov/data-api/api
#
CT_GOV_STUDIES = "https://clinicaltrials.gov/api/v2/studies"

#
# MyVariant.info API
# https://docs.myvariant.info/
#
MYVARIANT_BASE_URL = "https://myvariant.info/v1"
