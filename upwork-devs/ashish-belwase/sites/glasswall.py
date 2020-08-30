import logging
from random import randrange
from helper import Helper
from .base import BaseSite

log = logging.getLogger("GW:traffic_g")


class Glasswallsolutions(BaseSite):

    Allowed_Methods = BaseSite.Allowed_Methods + [
        "products",
        "pricing",
        "company",
        "random_click",
    ]

    def get_rand_action():
        return Glasswallsolutions.Allowed_Methods[
            randrange(0, len(Glasswallsolutions.Allowed_Methods))
        ]

    @staticmethod
    async def download_pdf(page, url):
        doc = await BaseSite.get_page(page, url)
        pdfs = doc.find('a[href*=".pdf"]')
        log.info("downloading {} pdfs".format(len(pdfs)))
        all_pdfs = []
        for pdf in pdfs:
            url = pdf.get("href")
            all_pdfs.append(url)
            Helper.get_file_from_url(url)
        return all_pdfs

    @staticmethod
    async def download(page, url):
        await Glasswallsolutions.download_pdf(page, url + "/technology")

    @staticmethod
    async def products(page, url):
        doc = await BaseSite.get_page(page, url + "/products")
        products = doc.find("div.product_card")
        return products

    @staticmethod
    async def pricing(page, url):
        doc = await BaseSite.get_page(page, url + "/pricing")
        pricing = doc.find("div.pricing_col")
        return pricing

    @staticmethod
    async def company(page, url):
        doc = await BaseSite.get_page(page, url + "/company")
        team = doc.find("div.team__profile__tile")
        return team

    @staticmethod
    async def random_click(page, url):
        doc = await BaseSite.get_page(page, url)
        buttons = await page.querySelectorAll("a[class^='btn'],a.button")
        btn = buttons[randrange(0, len(buttons))]
        if not await BaseSite.wait_for_element(btn):
            return

        await btn.click()
        await page.waitFor(BaseSite.DEFAULT_PAGE_WAIT)
        # await page.screenshot({"path": "page2.png"})
