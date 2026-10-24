/* Deployment facts that are not known until publication. Fill these in once; every page reads them.
   Leave a value null while it is unknown: the pages then show the fact as pending instead of a wrong link. */
window.COPEER_CONFIG = {
  repoUrl: 'https://github.com/qqliu/CoPEER',  /* links into the evidence release use <repoUrl>/blob/main/<path> */
  repoBranch: 'main',
  arxivId: null,            /* e.g. "2610.12345" once the preprint is posted */
  paperPdf: 'downloads/co-peer.pdf',
  paperSource: 'downloads/co-peer-arxiv-source.tar.gz',
  sourceCommit: '444d8f7'
};
