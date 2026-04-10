import scrapy

class GithubDeepSpider(scrapy.Spider):
    name = 'github'
    start_urls = ['https://github.com/trungvdhp?tab=repositories']

    def parse(self, response):
        for repo in response.css('li[itemprop="owns"]'):
            name = repo.css('a[itemprop="name codeRepository"]::text').get().strip()
            item = {
                'URL': response.urljoin(repo.css('a[itemprop="name codeRepository"]::attr(href)').get()),
                'About': repo.css('p[itemprop="description"]::text').get(default=name).strip(),
                'Last_Updated': repo.css('relative-time::attr(datetime)').get()
            }
            yield scrapy.Request(item['URL'], callback=self.parse_repo_details, meta={'item': item})

    def parse_repo_details(self, response):
        item = response.meta['item']
        langs = response.css('ul.list-style-none span.color-fg-default.text-bold::text').getall()
        item['Languages'] = ", ".join(langs) if langs else 'None'
        commit_text = response.css('span.fgColor-default::text').get()
        
        if commit_text and "Commits" in commit_text:
            item['Commits'] = commit_text.replace('Commits', '').strip()
        else:
            item['Commits'] = response.css('span.prc-Button-Label-FWkx3 span::text').get(default='None').strip()

        yield item