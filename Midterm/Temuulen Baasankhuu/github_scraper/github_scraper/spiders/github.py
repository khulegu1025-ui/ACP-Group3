import scrapy
from github_scraper.items import GithubRepoItem


class GithubSpider(scrapy.Spider):
    name = "github"

    def start_requests(self):
        url = "https://github.com/FelizJueves56?tab=repositories"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        repos = response.css("h3.wb-break-all a")

        for repo in repos:
            repo_url = response.urljoin(repo.attrib["href"])
            yield scrapy.Request(repo_url, callback=self.parse_repo)

    def parse_repo(self, response):

        item = GithubRepoItem()

        item["url"] = response.url

        about = response.css("p.f4::text").get()
        if about:
            item["about"] = about.strip()
        else:
            repo_name = response.css("strong.mr-2 a::text").get()
            item["about"] = repo_name

        item["last_updated"] = response.css("relative-time::attr(datetime)").get()

        languages = response.css("li.d-inline span::text").getall()
        languages = ", ".join([l.strip() for l in languages if l.strip()])
        item["languages"] = languages if languages else None

        commits = response.xpath("//a[contains(@href,'commits')]/span/text()").re_first(r"\d+")
        item["commits"] = commits if commits else None

        # EMPTY CHECK
        if not item["commits"] and not item["languages"]:
            item["about"] = None
            item["last_updated"] = None
            item["languages"] = None
            item["commits"] = None

        yield item