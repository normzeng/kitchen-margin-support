"""Validate the same static site at its branded and GitHub Pages addresses."""
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
BRANDED = "https://kitchenmargin.blackvaletechnologies.com/"
ORIGINS = (BRANDED, "https://normzeng.github.io/kitchen-margin-support/")
REQUIRED_ROUTES = {
    "", "support/", "privacy/", "privacy.html", "guides/latte-cost/",
    "ko/", "ko/support/", "ko/privacy/", "ko/guides/latte-cost/",
    "zh-Hant/", "zh-Hant/support/", "zh-Hant/privacy/",
}


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.lang = None
        self.ids = set()
        self.links = []
        self.canonical = []
        self.metadata_urls = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical.append(attrs["href"])
        elif tag == "link" and attrs.get("rel") == "alternate":
            self.metadata_urls.append(attrs["href"])
        elif "href" in attrs:
            self.links.append(attrs["href"])
        for attr in ("src", "poster"):
            if attr in attrs:
                self.links.append(attrs[attr])
        if tag == "meta" and attrs.get("property") in ("og:url", "og:image"):
            self.metadata_urls.append(attrs["content"])
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "refresh":
            self.links.append(attrs["content"].split("url=", 1)[1])


def route(path):
    return str(path.relative_to(ROOT)).removesuffix("index.html")


def target(path):
    result = ROOT / unquote(path)
    return result / "index.html" if result.is_dir() else result


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {path: Page(path) for path in ROOT.rglob("*.html")}

    def test_required_routes_and_hosting(self):
        actual = {route(path) for path in self.pages}
        self.assertTrue(REQUIRED_ROUTES <= actual, f"Missing routes: {REQUIRED_ROUTES - actual}")
        self.assertTrue((ROOT / ".nojekyll").is_file())
        self.assertFalse((ROOT / "CNAME").exists(), "The proxy needs the GitHub origin without a custom domain")

    def test_metadata(self):
        for path, page in self.pages.items():
            with self.subTest(page=route(path)):
                relative = route(path)
                canonical = "privacy/" if relative == "privacy.html" else relative
                self.assertEqual(page.canonical, [BRANDED + canonical])
                language = "zh-Hant-TW" if relative.startswith("zh-Hant/") else "ko" if relative.startswith("ko/") else "en"
                self.assertEqual(page.lang, language)
                if relative != "privacy.html":
                    self.assertIn("main", page.ids)
                for url in page.metadata_urls:
                    self.assertTrue(url.startswith(BRANDED), url)
                    self.assertTrue(target(url.removeprefix(BRANDED)).is_file(), url)

    def test_links_on_both_hosts(self):
        product_hosts = {urlsplit(origin).netloc for origin in ORIGINS}
        for origin in ORIGINS:
            base = urlsplit(origin)
            for path, page in self.pages.items():
                for reference in page.links:
                    with self.subTest(origin=origin, page=route(path), link=reference):
                        resolved = urlsplit(urljoin(origin + route(path), reference))
                        if resolved.netloc not in product_hosts:
                            continue
                        self.assertEqual(resolved.netloc, base.netloc, "Navigation must stay on the current host")
                        self.assertTrue(resolved.path.startswith(base.path), "Link escaped the GitHub project prefix")
                        destination = target(resolved.path.removeprefix(base.path))
                        self.assertTrue(destination.is_file(), str(destination))
                        if resolved.fragment:
                            self.assertIn(unquote(resolved.fragment), self.pages[destination].ids)

    def test_sitemap_and_robots(self):
        urls = [node.text for node in ET.parse(ROOT / "sitemap.xml").iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        expected = {BRANDED + route(path) for path in self.pages if route(path) != "privacy.html"}
        self.assertEqual(set(urls), expected)
        self.assertEqual(len(urls), len(expected), "Duplicate sitemap entries")
        self.assertIn("Sitemap: " + BRANDED + "sitemap.xml", (ROOT / "robots.txt").read_text().splitlines())


if __name__ == "__main__":
    unittest.main()
