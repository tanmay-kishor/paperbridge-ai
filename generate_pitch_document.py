"""
PaperBridge AI - Pitch Dossier & Viva Defense Word Document Generator
Creates a native, professional Word (.docx) document containing the complete pitch,
core features, USP, competitive matrix, viva presentation script, and examiner Q&A.
"""

import zipfile
import html
import os
import sys

def escape_xml(text):
    if text is None:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))

class DocxBuilder:
    def __init__(self):
        self.paragraphs = []

    def add_title(self, text, subtitle=None, meta=None):
        xml = f"""
        <w:p>
          <w:pPr>
            <w:pStyle w:val="Title"/>
            <w:spacing w:before="360" w:after="120"/>
            <w:jc w:val="center"/>
          </w:pPr>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
              <w:b/>
              <w:sz w:val="48"/>
              <w:color w:val="1E3A8A"/>
            </w:rPr>
            <w:t>{escape_xml(text)}</w:t>
          </w:r>
        </w:p>
        """
        self.paragraphs.append(xml)

        if subtitle:
            xml_sub = f"""
            <w:p>
              <w:pPr>
                <w:pStyle w:val="Subtitle"/>
                <w:spacing w:before="60" w:after="180"/>
                <w:jc w:val="center"/>
              </w:pPr>
              <w:r>
                <w:rPr>
                  <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                  <w:i/>
                  <w:sz w:val="26"/>
                  <w:color w:val="475569"/>
                </w:rPr>
                <w:t>{escape_xml(subtitle)}</w:t>
              </w:r>
            </w:p>
            """
            self.paragraphs.append(xml_sub)

        if meta:
            xml_meta = f"""
            <w:p>
              <w:pPr>
                <w:spacing w:before="60" w:after="280"/>
                <w:jc w:val="center"/>
              </w:pPr>
              <w:r>
                <w:rPr>
                  <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                  <w:sz w:val="20"/>
                  <w:color w:val="64748B"/>
                </w:rPr>
                <w:t>{escape_xml(meta)}</w:t>
              </w:r>
            </w:p>
            """
            self.paragraphs.append(xml_meta)

    def add_heading_1(self, text):
        xml = f"""
        <w:p>
          <w:pPr>
            <w:pStyle w:val="Heading1"/>
            <w:spacing w:before="320" w:after="140"/>
            <w:pBdr>
              <w:bottom w:val="single" w:sz="12" w:space="4" w:color="1E3A8A"/>
            </w:pBdr>
          </w:pPr>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
              <w:b/>
              <w:sz w:val="34"/>
              <w:color w:val="1E3A8A"/>
            </w:rPr>
            <w:t>{escape_xml(text)}</w:t>
          </w:r>
        </w:p>
        """
        self.paragraphs.append(xml)

    def add_heading_2(self, text):
        xml = f"""
        <w:p>
          <w:pPr>
            <w:pStyle w:val="Heading2"/>
            <w:spacing w:before="240" w:after="80"/>
          </w:pPr>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
              <w:b/>
              <w:sz w:val="26"/>
              <w:color w:val="0F766E"/>
            </w:rPr>
            <w:t>{escape_xml(text)}</w:t>
          </w:r>
        </w:p>
        """
        self.paragraphs.append(xml)

    def add_heading_3(self, text):
        xml = f"""
        <w:p>
          <w:pPr>
            <w:pStyle w:val="Heading3"/>
            <w:spacing w:before="160" w:after="60"/>
          </w:pPr>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
              <w:b/>
              <w:sz w:val="22"/>
              <w:color w:val="1E293B"/>
            </w:rPr>
            <w:t>{escape_xml(text)}</w:t>
          </w:r>
        </w:p>
        """
        self.paragraphs.append(xml)

    def add_paragraph(self, text, bold_prefix=None, italic=False):
        runs = []
        if bold_prefix:
            runs.append(f"""
            <w:r>
              <w:rPr>
                <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                <w:b/>
                <w:sz w:val="22"/>
                <w:color w:val="0F172A"/>
              </w:rPr>
              <w:t>{escape_xml(bold_prefix)}</w:t>
            </w:r>
            """)
        runs.append(f"""
        <w:r>
          <w:rPr>
            <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
            {'<w:i/>' if italic else ''}
            <w:sz w:val="22"/>
            <w:color w:val="334155"/>
          </w:rPr>
          <w:t xml:space="preserve">{escape_xml(text)}</w:t>
        </w:r>
        """)
        xml = f"""
        <w:p>
          <w:pPr>
            <w:spacing w:before="40" w:after="100" w:line="276" w:lineRule="auto"/>
          </w:pPr>
          {''.join(runs)}
        </w:p>
        """
        self.paragraphs.append(xml)

    def add_callout(self, text, bold_title="KEY TAKEAWAY:"):
        xml = f"""
        <w:tbl>
          <w:tblPr>
            <w:tblW w:w="0" w:type="auto"/>
            <w:tblBorders>
              <w:top w:val="none"/>
              <w:left w:val="single" w:sz="36" w:space="0" w:color="0F766E"/>
              <w:bottom w:val="none"/>
              <w:right w:val="none"/>
            </w:tblBorders>
            <w:tblCellMar>
              <w:top w:w="120" w:type="dxa"/>
              <w:left w:w="180" w:type="dxa"/>
              <w:bottom w:w="120" w:type="dxa"/>
              <w:right w:w="180" w:type="dxa"/>
            </w:tblCellMar>
          </w:tblPr>
          <w:tr>
            <w:tc>
              <w:tcPr>
                <w:tcW w:w="9360" w:type="dxa"/>
                <w:shd w:val="clear" w:color="auto" w:fill="F0FDF4"/>
              </w:tcPr>
              <w:p>
                <w:pPr>
                  <w:spacing w:before="40" w:after="40" w:line="260" w:lineRule="auto"/>
                </w:pPr>
                <w:r>
                  <w:rPr>
                    <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                    <w:b/>
                    <w:sz w:val="22"/>
                    <w:color w:val="0F766E"/>
                  </w:rPr>
                  <w:t>{escape_xml(bold_title)} </w:t>
                </w:r>
                <w:r>
                  <w:rPr>
                    <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                    <w:sz w:val="22"/>
                    <w:color w:val="1E293B"/>
                  </w:rPr>
                  <w:t>{escape_xml(text)}</w:t>
                </w:r>
              </w:p>
            </w:tc>
          </w:tr>
        </w:tbl>
        <w:p><w:pPr><w:spacing w:before="60" w:after="60"/></w:pPr></w:p>
        """
        self.paragraphs.append(xml)

    def add_bullet(self, bold_term, description):
        xml = f"""
        <w:p>
          <w:pPr>
            <w:pStyle w:val="ListParagraph"/>
            <w:spacing w:before="40" w:after="80" w:line="260" w:lineRule="auto"/>
            <w:ind w:left="480" w:hanging="240"/>
          </w:pPr>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
              <w:color w:val="0F766E"/>
              <w:b/>
            </w:rPr>
            <w:t>✦ </w:t>
          </w:r>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
              <w:b/>
              <w:sz w:val="22"/>
              <w:color w:val="0F172A"/>
            </w:rPr>
            <w:t>{escape_xml(bold_term)}: </w:t>
          </w:r>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
              <w:sz w:val="22"/>
              <w:color w:val="334155"/>
            </w:rPr>
            <w:t>{escape_xml(description)}</w:t>
          </w:r>
        </w:p>
        """
        self.paragraphs.append(xml)

    def add_table(self, headers, rows):
        col_w = int(9360 / len(headers))
        table_xml = ["""
        <w:tbl>
          <w:tblPr>
            <w:tblW w:w="9360" w:type="dxa"/>
            <w:tblBorders>
              <w:top w:val="single" w:sz="8" w:space="0" w:color="CBD5E1"/>
              <w:left w:val="none"/>
              <w:bottom w:val="single" w:sz="8" w:space="0" w:color="CBD5E1"/>
              <w:right w:val="none"/>
              <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
              <w:insideV w:val="none"/>
            </w:tblBorders>
            <w:tblCellMar>
              <w:top w:w="120" w:type="dxa"/>
              <w:left w:w="140" w:type="dxa"/>
              <w:bottom w:w="120" w:type="dxa"/>
              <w:right w:w="140" w:type="dxa"/>
            </w:tblCellMar>
          </w:tblPr>
        """]

        # Header Row
        table_xml.append("<w:tr>")
        for h in headers:
            table_xml.append(f"""
            <w:tc>
              <w:tcPr>
                <w:tcW w:w="{col_w}" w:type="dxa"/>
                <w:shd w:val="clear" w:color="auto" w:fill="1E3A8A"/>
              </w:tcPr>
              <w:p>
                <w:pPr><w:spacing w:before="60" w:after="60"/></w:pPr>
                <w:r>
                  <w:rPr>
                    <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                    <w:b/>
                    <w:sz w:val="20"/>
                    <w:color w:val="FFFFFF"/>
                  </w:rPr>
                  <w:t>{escape_xml(h)}</w:t>
                </w:r>
              </w:p>
            </w:tc>
            """)
        table_xml.append("</w:tr>")

        # Data Rows
        for r_idx, r in enumerate(rows):
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            table_xml.append("<w:tr>")
            for cell in r:
                table_xml.append(f"""
                <w:tc>
                  <w:tcPr>
                    <w:tcW w:w="{col_w}" w:type="dxa"/>
                    <w:shd w:val="clear" w:color="auto" w:fill="{bg}"/>
                  </w:tcPr>
                  <w:p>
                    <w:pPr><w:spacing w:before="40" w:after="40"/></w:pPr>
                    <w:r>
                      <w:rPr>
                        <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                        <w:sz w:val="20"/>
                        <w:color w:val="334155"/>
                      </w:rPr>
                      <w:t>{escape_xml(cell)}</w:t>
                    </w:r>
                  </w:p>
                </w:tc>
                """)
            table_xml.append("</w:tr>")

        table_xml.append("</w:tbl>")
        table_xml.append('<w:p><w:pPr><w:spacing w:before="60" w:after="120"/></w:pPr></w:p>')
        self.paragraphs.append("".join(table_xml))

    def build_xml(self):
        body_content = "".join(self.paragraphs)
        xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document mc:Ignorable="w14 w15 wp14" xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">
<w:body>
{body_content}
<w:sectPr>
  <w:pgSz w:w="12240" w:h="15840" w:orient="portrait"/>
  <w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080" w:header="708" w:footer="708" w:gutter="0"/>
  <w:pgNumType/>
  <w:docGrid w:linePitch="360"/>
</w:sectPr>
</w:body>
</w:document>"""
        return xml

def generate_pitch_document():
    doc = DocxBuilder()

    # Title & Header
    doc.add_title(
        "PaperBridge AI",
        subtitle="Academic Pitch Dossier & Viva Defense Guide",
        meta="B.Tech Computer Science & Engineering / Artificial Intelligence | Project 2026 Team Handout"
    )

    doc.add_callout(
        "\"PaperBridge AI is an accessibility-first academic research engine that solves two major bottlenecks in student literature reviews: the paywall dead-end and cognitive reading difficulty.\"",
        bold_title="THE ELEVATOR PITCH:"
    )

    # 1. The Core Problem
    doc.add_heading_1("1. The Problem Landscape: Where Traditional Search Engines Fail")
    doc.add_paragraph("Traditional academic discovery platforms like Google Scholar, IEEE Xplore, and PubMed are designed around commercial institutional access and raw citation popularity. For undergraduate students, early-stage researchers, and independent scholars, this paradigm creates two severe systemic friction points:")

    doc.add_bullet(
        "The Paywall Dead-End (Financial Access Barrier)",
        "A student invests hours formulating queries, discovers the exact foundational paper needed, clicks the link, and encounters a $35 to $45 publisher paywall (Elsevier, Springer, IEEE). Commercial search engines offer zero recovery: the student is left stranded with no legal pathway forward."
    )
    doc.add_bullet(
        "Cognitive Overwhelm & Reading Level Blindness (Comprehension Barrier)",
        "Algorithms like Google Scholar rank results predominantly by PageRank and cumulative citation count. Consequently, the top results are heavily skewed toward dense, mathematically intense seminal papers from 2015-2018. An undergraduate exploring a new topic has no mechanism to distinguish introductory survey papers from doctoral-level treatises."
    )
    doc.add_bullet(
        "The Lexical Synonym Trap (Search Quality Barrier)",
        "Keyword-based lexical search fails whenever researchers and authors use varying terminology for the same underlying concept (e.g., 'temporal sequence forecasting' vs. 'time-series prediction')."
    )

    # 2. What Makes Us Distinct / USP
    doc.add_heading_1("2. Unique Value Proposition (USP) & Market Differentiation")
    doc.add_paragraph("PaperBridge AI's core architectural philosophy is: 'Meeting the researcher halfway.' Rather than assuming the user has an enterprise library proxy and a doctorate, PaperBridge AI actively validates whether a paper is legally readable and evaluates its cognitive readability score.")

    doc.add_callout(
        "Our USP is Algorithmic Recovery: If a paper is paywalled, PaperBridge AI does NOT stop. It dynamically executes a secondary credibility filter to locate legitimate, same-author open preprints or bibliographically linked open alternatives.",
        bold_title="THE CORE DIFFERENTIATOR:"
    )

    # Competitive Table
    headers = ["Feature / Capability", "Google Scholar", "Research Rabbit / Connected Papers", "PaperBridge AI"]
    rows = [
        ["Discovery Model", "Lexical keywords & PageRank citation count", "Visual citation graphs & author clustering", "Dense citation-graph embeddings (allenai-specter)"],
        ["Paywall Handling", "Shows paywalled link; leaves user stranded", "Visualizes paywalled nodes; cannot open text", "Automatic fallback to legal same-author preprints / shared references"],
        ["Reading Level", "None (assumes expert reader)", "None", "Flesch-Kincaid & jargon density (Foundational / Intermediate / Advanced)"],
        ["Open-Access Verification", "Unverified external web links", "Limited to DOI metadata", "Dual-pass legal verification via Unpaywall & OpenAlex (zero piracy)"],
        ["Cloud Architecture", "Proprietary mega-datacenter", "SaaS commercial platform", "Adaptive dual-mode: 768-d SPECTER + Scikit-Learn TF-IDF low-memory fallback"]
    ]
    doc.add_table(headers, rows)

    # 3. Core Architectural Pillars
    doc.add_heading_1("3. The 4 Core Architectural & Technical Features")
    doc.add_paragraph("PaperBridge AI is built on a modular four-tier pipeline combining transformer embeddings, bibliometrics, readability scoring, and multi-source API federation:")

    doc.add_heading_2("Pillar 1: Citation-Informed Semantic Discovery (allenai-specter)")
    doc.add_bullet(
        "Scientific Graph Pretraining",
        "Unlike generic sentence transformers (such as MiniLM) trained on generic web sentences, SPECTER is pretrained on scientific citation graphs. Papers that domain experts cite together are mapped closer in the 768-dimensional latent vector space, measuring true scholarly intent over surface vocabulary."
    )
    doc.add_bullet(
        "Adaptive Cloud Headroom Guard",
        "To guarantee 100% uptime on memory-constrained cloud environments (such as Render's 512MB free tier), the pipeline includes an automatic RAM threshold detector (is_low_memory_env). If available memory drops below 1200MB, it transitions seamlessly to a Scikit-Learn TF-IDF cosine similarity engine consuming under 30MB of RAM."
    )

    doc.add_heading_2("Pillar 2: Quad-Tier Resilient Academic Data Federation")
    doc.add_paragraph("To protect against commercial API rate limits (HTTP 429) during live usage, PaperBridge AI executes a cascading 4-tier discovery strategy:")
    doc.add_bullet("Tier 1: Semantic Scholar Graph API", "Primary academic index with rich citation metadata and field-of-study tags.")
    doc.add_bullet("Tier 2: OpenAlex API", "Open catalog of 250M+ scientific works offering 100,000 free requests per day in the polite pool, providing instant fallback when Semantic Scholar throttles.")
    doc.add_bullet("Tier 3: Cornell arXiv API", "Live real-time preprint discovery providing permanent open-access PDF links.")
    doc.add_bullet("Tier 4: Offline Benchmark Datasets", "Guarantees graceful degradation even during total network loss.")

    doc.add_heading_2("Pillar 3: Legitimate Dual-Pass Open-Access Verification")
    doc.add_bullet(
        "Unpaywall & OpenAlex Integration",
        "Queries over 50,000 global institutional repositories (PubMed Central, university digital commons, preprint servers) to verify legitimate publisher-compliant 'Green' and 'Gold' Open Access versions. Strictly zero piracy (no Sci-Hub scraping); all returned PDFs are legally authorized."
    )

    doc.add_heading_2("Pillar 4: Algorithmic Paywall-Fallback & Credibility Filter")
    doc.add_paragraph("When a requested paper is paywalled, PaperBridge AI triggers its credibility filter to surface an accessible 'Related Work' recommendation:")
    doc.add_bullet("Same-Author Match (Highest Confidence)", "Verifies whether the original authors uploaded an open preprint of the exact work to arXiv or an institutional repository (tagged: '✦ same author').")
    doc.add_bullet("Bibliographic Reference Overlap", "Analyzes shared reference citations. Open papers that cite the same foundational literature are surfaced (tagged: '✦ N shared references').")
    doc.add_bullet("Quality Floor Enforcement", "Enforces minimum citation thresholds and shared field-of-study tags, preventing low-quality or irrelevant preprints from polluting results.")

    doc.add_heading_2("Pillar 5: Cognitive Readability & Jargon Scorer")
    doc.add_bullet(
        "Multivariate Readability Metric",
        "Extracts word length, sentence complexity, and domain-specific terminology density to compute a Flesch-Kincaid grade level. Papers are cleanly classified into Foundational (accessible introductions), Intermediate (standard journal papers), and Advanced (heavy mathematical/theoretical treatises)."
    )

    # 4. Target Audience
    doc.add_heading_1("4. Target Audience & Practical Stakeholders")
    doc.add_bullet("Undergraduate & Master's Students", "Students conducting literature surveys, seminar reports, and capstone theses without institutional access from off-campus.")
    doc.add_bullet("Interdisciplinary Researchers", "Specialists exploring unfamiliar domains (e.g., clinicians needing foundational machine learning papers, or computer scientists reading bioinformatics) who need readability-guided entry points.")
    doc.add_bullet("Independent Scholars & Citizen Scientists", "Educators, independent developers, and researchers without institutional library subscriptions.")

    # 5. Viva Presentation Script
    doc.add_heading_1("5. Viva & Project Presentation Script (Word-for-Word Speaking Guide)")
    doc.add_paragraph("Use this timed structure for your 3-minute project presentation:")

    doc.add_heading_2("Phase 1: The Hook & Introduction (0:00 - 0:30)")
    doc.add_paragraph("\"Good morning, respected evaluators. Today, we are presenting PaperBridge AI—an accessibility-first academic research platform engineered to eliminate the financial and cognitive barriers in scientific literature discovery.\"", italic=True)

    doc.add_heading_2("Phase 2: The Two Systemic Failures (0:30 - 1:15)")
    doc.add_paragraph("\"When undergraduate students start a literature review on platforms like Google Scholar, they immediately hit two walls. First is the Paywall Dead-End: finding a seminal paper only to be blocked by a $40 publisher fee. Second is Cognitive Overwhelm: search engines rank papers strictly by citation count, presenting mathematically dense, advanced doctoral papers to beginners with zero reading-level guidance.\"", italic=True)

    doc.add_heading_2("Phase 3: The PaperBridge AI Solution (1:15 - 2:30)")
    doc.add_paragraph("\"PaperBridge AI solves both bottlenecks algorithmically through a four-part pipeline:\n"
                      "1. Semantic Intent: We use AllenAI's SPECTER model, which embeds papers based on scientific citation networks rather than surface keywords.\n"
                      "2. Verified Legal Access: We cross-reference Unpaywall and OpenAlex across 50,000 global repositories to uncover legal free copies.\n"
                      "3. The Paywall Fallback Filter: When a paper is paywalled, our system doesn't stop. It evaluates same-author preprints and bibliographic reference overlap to recommend credible open alternatives.\n"
                      "4. Readability Tiers: We analyze linguistic complexity and jargon density, labeling papers as Foundational, Intermediate, or Advanced so researchers can climb the literature ladder step-by-step.\"", italic=True)

    doc.add_heading_2("Phase 4: Conclusion & Closing Stance (2:30 - 3:00)")
    doc.add_paragraph("\"Our system is deployed live on Vercel and Render, operating with a quad-tier fallback architecture connecting Semantic Scholar, OpenAlex, and arXiv. In summary, PaperBridge AI is built on a simple premise: academic search shouldn't just index papers—it should find research you can legitimately access and understand right now. Thank you, and we welcome your questions.\"", italic=True)

    # 6. Anticipated Viva Questions
    doc.add_heading_1("6. Anticipated Examiner Questions & Model Answers")

    doc.add_heading_3("Q1: Why did you choose SPECTER over a generic model like all-MiniLM-L6-v2?")
    doc.add_paragraph("Model Answer: \"Generic sentence transformers are trained on general web text and conversational pairs. In scientific literature, two papers may share surface vocabulary while addressing completely different depths, or use different vocabularies for related concepts. SPECTER is trained directly on academic citation graphs—papers that researchers cite together are pulled closer in vector space. This ensures our similarity scores reflect genuine scholarly relatedness rather than superficial keyword matching.\"")

    doc.add_heading_3("Q2: How do you prevent low-quality or predatory preprints from being recommended as paywall fallbacks?")
    doc.add_paragraph("Model Answer: \"We implement a multi-factor credibility filter in open_access.py. A fallback candidate is only surfaced if it meets strict quality criteria: (1) Same-author verification (the authors' own preprint), (2) Minimum citation count threshold, (3) Shared field-of-study taxonomy, or (4) A minimum bibliographic reference overlap. This guarantees that similarity alone never surfaces irrelevant or unverified papers.\"")

    doc.add_heading_3("Q3: Does your platform scrape pirated websites like Sci-Hub?")
    doc.add_paragraph("Model Answer: \"No, absolutely not. PaperBridge AI enforces 100% legal compliance. We query legitimate Open Access APIs—Unpaywall and OpenAlex—which index authorized institutional repositories, PubMed Central, and publisher open-access repositories (Green and Gold Open Access). We uncover legally authorized preprints and author manuscripts that students often do not realize exist.\"")

    doc.add_heading_3("Q4: How does your system operate without crashing on cloud containers with limited RAM (e.g. 512MB)?")
    doc.add_paragraph("Model Answer: \"Dense transformer models require substantial RAM during tensor operations. In backend/pipeline/embeddings.py, we implemented an adaptive memory detection function (is_low_memory_env). When running on Render or low-memory cloud instances, the system automatically transitions to a lightweight Scikit-Learn TF-IDF cosine similarity engine that consumes less than 30MB of RAM and executes in ~2 milliseconds, guaranteeing 100% cloud container uptime.\"")

    doc.add_heading_3("Q5: What happens if an external academic API like Semantic Scholar is down or rate-limited?")
    doc.add_paragraph("Model Answer: \"We engineered a Quad-Tier Failover Architecture in metadata.py. If Semantic Scholar returns an HTTP 429 rate-limit error, our pipeline immediately delegates to OpenAlex (100,000 free queries/day). If OpenAlex is unavailable, it queries the Cornell arXiv API for live preprints. If the host is completely offline, it gracefully serves benchmark sample datasets. The end user never experiences a broken search.\"")

    # Output file creation
    output_filename = "PaperBridge_AI_Pitch_and_Viva_Defense_Dossier.docx"
    output_path = os.path.join(os.getcwd(), output_filename)
    template_docx = "PaperBridge_AI_Updated_Project_Document_v3.docx"

    with zipfile.ZipFile(template_docx, 'r') as zin:
        with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == 'word/document.xml':
                    zout.writestr(item, doc.build_xml().encode('utf-8'))
                else:
                    zout.writestr(item, zin.read(item.filename))

    print(f"SUCCESS: Generated {output_filename} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    generate_pitch_document()
