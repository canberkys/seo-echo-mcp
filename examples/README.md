# Examples

Realistic output artifacts so you can preview what the tools emit before you install.

| File | What it is |
|------|------------|
| [`site_profile.json`](site_profile.json) | `analyze_site("example-tech-blog.test")` output — the voice profile fed into every downstream tool |
| [`outline.json`](outline.json) | `generate_outline("kubernetes ingress", site_profile)` output |
| [`audit_report.json`](audit_report.json) | `audit_content(draft_md, site_profile, target_keyword)` output with 8 checks passed / 3 warnings |
| [`draft_skeleton.md`](draft_skeleton.md) | `prepare_draft_skeleton(outline, site_profile, faq_section, schema_jsonld)` output — the `<!-- WRITE -->` directives are what the host LLM fills |
| [`content_gap_report.json`](content_gap_report.json) | `detect_content_gaps(site, competitors)` output — topics missing from the site |

All artifacts are anonymized from real runs on a technical blog. URLs and post titles are synthetic.
