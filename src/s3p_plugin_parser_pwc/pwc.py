import datetime
import time

from s3p_sdk.plugin.payloads.parsers import S3PParserBase
from s3p_sdk.types import S3PRefer, S3PDocument, S3PPlugin
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

import re

import dateutil.parser


class PWC(S3PParserBase):
    """
    A Parser payload that uses S3P Parser base class.
    """
    HOST = 'https://www.pwc.com'

    def __init__(self, refer: S3PRefer, plugin: S3PPlugin, web_driver: WebDriver, max_count_documents: int = None,
                 last_document: S3PDocument = None):
        super().__init__(refer, plugin, max_count_documents, last_document)

        # Тут должны быть инициализированы свойства, характерные для этого парсера. Например: WebDriver
        self._driver = web_driver
        self._wait = WebDriverWait(self._driver, timeout=20)

    def _parse(self):
        """
        Метод, занимающийся парсингом. Он добавляет в _content_document документы, которые получилось обработать
        :return:
        :rtype:
        """
        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter to {self.HOST}")

        # ========================================
        # Тут должен находится блок кода, отвечающий за парсинг конкретного источника
        # -
        self._driver.set_page_load_timeout(40)

        markets_link = 'https://www.pwc.com/gx/en/industries/consumer-markets/publications.html'
        industries_link = 'https://www.pwc.com/gx/en/industries/tmt/publications.html'
        research_link = 'https://www.pwc.com/gx/en/industries/financial-services/publications.html'

        docs = []
        docs.extend(self._collect_links_from_publications_page(markets_link))
        docs.extend(self._collect_links_from_publications_page(industries_link))
        # docs.extend(self._collect_links_from_publications_page(research_link))

        for doc in docs:
            self._parse_publication(doc)
        # ---
        # ========================================

    def _collect_links_from_publications_page(self, url: str):
        self._initial_access_source(url)
        self.logger.debug(f'Start collect publications from {url}')

        docs = []

        try:
            results_e = self._driver.find_element(By.CLASS_NAME, 'results').text
            results = int(re.match(r'(\d+).*', results_e).groups()[0])
            print(results)
        except Exception as e:
            self.logger.error(e)

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # ВОТ ТУТ НУЖНО ВСТАВИТЬ ДОКАЧКУ ФАЙЛОВ ПРИ ПОМОЩИ КНОКИ MORE.
        # ............................................................
        # Сейчас статьи не докачиваются...
        time.sleep(6)
        articles = self._driver.find_elements(By.CLASS_NAME, 'collection__item-link')
        print(len(articles))

        for index, article in enumerate(articles):
            # Ограничение парсинга до установленного параметра self.max_count_documents
            # if index >= self._max_count_documents:
            #     self.logger.debug(f'Max count articles reached ({self._max_count_documents})')
            #     break

            try:
                href = article.get_attribute('href')
                date = article.find_element(By.TAG_NAME, 'time').text
                title = article.find_element(By.TAG_NAME, 'h4').text
                abstract = None

                try:
                    abstract = article.find_element(By.CLASS_NAME, 'paragraph').text
                except:
                    pass

                document = S3PDocument(None, title, abstract, None, href, None, None, dateutil.parser.parse(date), None)
                self.logger.debug(f'find new article {href}')
                docs.append(document)
            except Exception as e:
                self.logger.error(e)

        return docs

    def _parse_publication(self, doc: S3PDocument):
        self.logger.debug(f'Start parse publications at {doc.link}')
        try:
            self._initial_access_source(doc.link)
            time.sleep(2)

            text = self._driver.find_element(By.CLASS_NAME, 'container').text
            doc.text = text
            doc.load_date = datetime.datetime.now()

        except Exception as e:
            self.logger.error(e)

        self._find(doc)
        # print(doc.title)

    def _initial_access_source(self, url: str, delay: int = 2):
        self._driver.get(url)
        self.logger.debug('Entered on web page ' + url)
        time.sleep(delay)
        self._agree_cookie_pass()

    def _agree_cookie_pass(self):
        """
        Метод прожимает кнопку agree на модальном окне
        """
        cookie_agree_xpath = '//*[@id="onetrust-accept-btn-handler"]'

        try:
            cookie_button = self._driver.find_element(By.XPATH, cookie_agree_xpath)
            if WebDriverWait(self._driver, 5).until(ec.element_to_be_clickable(cookie_button)):
                cookie_button.click()
                self.logger.debug(F"Parser pass cookie modal on page: {self._driver.current_url}")
        except NoSuchElementException as e:
            self.logger.debug(f'modal agree not found on page: {self._driver.current_url}')
