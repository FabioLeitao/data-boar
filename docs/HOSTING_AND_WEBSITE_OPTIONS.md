# Hosting options: private repositories and public website

This memo supports the **Licensing, Enforcement, and GTM** program: where to host private issuer tooling, commercial modules, and a public marketing site. **Costs are indicative (2025–2026); confirm on each vendor’s pricing page.**

## Private source (issuer tooling, commercial modules)

| Option                                    | Access control                      | Indicative cost                                                       | Notes                                                                                       |
| ------                                    | --------------                      | ---------------                                                       | -----                                                                                       |
| **GitHub private repo** (personal or org) | Invite-only; branch protection; 2FA | **Free** on personal; **Team ~$4/user/mo** (org)                      | Fits `tools/license-studio` copied to a **separate private repo**; never push signing keys. |
| **GitHub Enterprise**                     | SSO, audit, IP allow                | **Enterprise pricing**                                                | When you need enterprise compliance features.                                               |
| **GitLab** (gitlab.com private group)     | Per-group permissions               | **Free** tier limited; **Premium** paid tiers for advanced compliance | Good if you prefer GitLab CI.                                                               |
| **Self-hosted Forgejo / Gitea**           | You operate network ACL             | **VPS ~$5–25/mo** + ops time                                          | Air-gappable; you patch the server.                                                         |

**Recommendation:** Start with **GitHub private repositories** under your existing org; keep the **issuer** repo off the public `data-boar` tree and never commit keys or blobs.

## Public website (pitch, contact, screenshots)

| Option                          | Indicative cost                             | Notes                                      |
| ------                          | ---------------                             | -----                                      |
| **Cloudflare Pages** + DNS      | **Free** tier often sufficient; Pro ~$20/mo | Static site from Git; global CDN.          |
| **GitHub Pages**                | **Free** for public repos                   | Simple; tie to a `www` repo.               |
| **Netlify / Vercel**            | **Free** hobby tiers                        | Similar to Cloudflare Pages.               |
| **Managed WordPress / Webflow** | ~$10–30/mo+                                 | Less engineer-friendly for “docs as code.” |

**Recommendation:** **Cloudflare Pages** or **GitHub Pages** for a static site; keep **canonical product truth** in the main app repo README/pitch; mirror short copy on the site with a **contact form** or `mailto:` / Calendly link.

**Future (not scheduled):** A richer **multilingual** site (pitch, use cases, how-tos, doc hub, release links) and **extra doc languages** (e.g. es, ja) are captured in **[plans/PLAN_WEBSITE_AND_DOCS_I18N_FUTURE.md](plans/PLAN_WEBSITE_AND_DOCS_I18N_FUTURE.md)** — activate closer to **production-ready** / GTM. **Important:** the **website’s technical depth** (full guides, scenarios, releases, roadmap fronts, Hub/GitHub links) is **intentionally heavier** than the **stakeholder pitch** or **presentation** — see that plan **§2.1** and sprint milestone **M-SITE-READY** in [SPRINTS_AND_MILESTONES.md](plans/SPRINTS_AND_MILESTONES.md). **Locale UX** on the site should align with **dashBOARd** i18n ([PLAN_DASHBOARD_I18N.md](plans/PLAN_DASHBOARD_I18N.md)).

## Contact and sales

- Put **one clear CTA** on the site: contact email, form, or booking link.
- Do **not** embed licensing secrets or issuer URLs in the public site.

## Related

- [LICENSING_OPEN_CORE_AND_COMMERCIAL.md](LICENSING_OPEN_CORE_AND_COMMERCIAL.md)
- [LICENSING_SPEC.md](LICENSING_SPEC.md)
- [RELEASE_INTEGRITY.md](RELEASE_INTEGRITY.md)
