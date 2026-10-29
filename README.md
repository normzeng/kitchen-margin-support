# Kitchen Margin website

This repository is the editable source for Kitchen Margin's public landing
pages, guides, support and privacy information. Keep changes here rather than
maintaining separate website copies alongside the app.

The canonical address is `https://kitchenmargin.blackvaletechnologies.com/`.
The product router serves this repository's GitHub Pages output at that host.
Pages also serves `https://normzeng.github.io/kitchen-margin-support/` from
`main`, repository root; merging to `main` automatically publishes the site.

## Compatibility

Keep the existing GitHub Pages routes and assets working: released apps, App
Store listings and external links still use them. Both hosts serve the same
content, with canonical metadata pointing to the branded host. Navigation and
assets use relative URLs so they work at both the branded root and GitHub's
project prefix. Keep the `privacy.html` alias and public GitHub issue intake.

Do not attach a Pages custom domain or add a `CNAME` file while the router
fetches this GitHub origin. Do not replace origin pages with redirects to the
branded host: the router would fetch its own redirects and create a loop.
The origin must retain full pages and assets.

English pages live at the root, Korean under `ko/` and Traditional Chinese
under `zh-Hant/`. Keep locale support/privacy URLs, canonical and alternate
links, the sitemap and robots declaration consistent when changing routes.
The existing Apple terms, subscription help and support-contact links remain
product-specific.

## Validation

Run before proposing a change:

```sh
python3 -m unittest discover -s tests
```

The standard-library checks cover required routes, local links, assets and
fragments on both host layouts, page languages, canonical/social metadata,
sitemap coverage and the no-custom-domain requirement. They do not contact
hosting or validate external services.

## Staged rollout and rollback

1. Merge the separate privacy-disclosure PR first and wait for Pages to
   publish it. Verify the English, Korean and Traditional Chinese policies
   distinguish the GitHub copy from branded marketing analytics and link to
   the Black Vale website privacy notice. The metadata PR must target `main`
   with the disclosure included before final review and publication.
2. Merge the router PR, then perform its separately approved manual
   deployment, pointing Kitchen Margin's branded host at the **currently
   published** support site. Verify root, support, privacy, existing locales
   and assets there. Check that slashless directory URLs redirect to the same
   branded host with a trailing slash, query strings survive, and video range
   requests work.
3. Only after those pages work at the branded host, merge the website PR.
   Pages publishes automatically; this promotes branded canonical URLs and
   adds the Chinese landing page. Verify the sitemap, locale navigation,
   `privacy.html` alias and existing GitHub URLs after Pages finishes.
4. Keep the GitHub origin available. Changes to app binaries, App Store
   metadata or other product websites are separate work.

For a website regression, revert its merge and let Pages republish while the
router continues serving the support-site origin. Verify both addresses.
If the router must also revert to the former placeholder origin, revert the
website metadata first; otherwise canonical support/privacy URLs would point
at pages that the placeholder cannot serve. Keep prior commits available and
do not remove compatibility routes during rollback.
Retain the website analytics disclosure while branded marketing analytics
remain active; reverting canonical metadata is not a reason to remove it.
