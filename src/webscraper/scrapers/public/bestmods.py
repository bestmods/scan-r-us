from ...base import Webscraper as BaseWebscraper

from debugger import debugMsg

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

from markdownify import markdownify as md

import re

from utils import ConvertToUrl

import base64

import requests

class Webscraper(BaseWebscraper):
    name = "Best Mods"
    url = "bestmods.io"
    
    def BaseWait(self):
        # Wait until we have coursel items.
        waitXpath = "//li[contains(@class, 'react-multi-carousel-item')]"
        
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((By.XPATH, waitXpath))
        )
    
    async def GatherQueries(self):
        queries: list[str] = []
        
        debugMsg(self.cfg, 3, f"[{self.tag} F] Sending request to sitemap.")
        
        # Send request to sitemap.
        try:
            reqUrl = f"{self.protocol}://{self.url}/sitemap.xml"
            
            self.driver.get(reqUrl)
            
            # Wait until <url> elements are available.
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "url")))
            
            soup = BeautifulSoup(self.driver.page_source, "lxml")
            
            if soup is None:
                debugMsg(self.cfg, 0, f"[{self.tag} F] Soup object is None.")
                
                return
            
            urls = []
            
            # Retrieve all 'url' elements.
            eles = soup.findAll("url")
            
            # Loop through each element and extract 'loc' and append it to 'urls' list.
            for ele in eles:
                urls.append(ele.loc.text)
                
            for url in urls:
                if "/mod/" not in url:
                    debugMsg(self.cfg, 4, f"[{self.tag} F] URL '{url}' doesn't contain /mod/. Ignoring...")
                    
                    continue
                
                debugMsg(self.cfg, 4, f"[{self.tag} F] Found URL => {url}")
                
                # Strip URL.
                query = url.replace(f"{self.protocol}://{self.url}", "")
                
                debugMsg(self.cfg, 4, f"[{self.tag} F] Query => {query}")
                
                # Add to queries list.
                queries.append(query)
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.tag} F] Error sending request to sitemap.")
            debugMsg(self.cfg, 0, e)
            
        return queries
        
    def ParseCategoryId(self, url, resp):
        id = None
        
        try:
            # Do match on URL.
            match = re.search("\/([A-Za-z0-9_-]+)\/mod\/[A-Za-z0-9_-]+", url)
            
            if not match:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse category ID. 'match' is falsey.")
                
                return id, False
            
            # Get first group.
            group = match.group(1)
            
            if not group:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse category ID. 'group' is falsey.")
                
                return id, False
            
            if group in self.cats:
                id = self.cats[group]
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.tag} P] Failed to parse category ID due to exception.")
            debugMsg(self.cfg, 0, e)
            
            return id, False
        
        return id, True
    
    def ParseViewUrl(self, url, resp):
        viewUrl = None
    
        try:
            soup = BeautifulSoup(resp, "html.parser")
            
            # Get title.
            div = soup.find("div", class_="flex flex-wrap justify-center gap-4")
            
            if div is None:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse view URL. 'div' is None.")
                
                return viewUrl, False
            
            h1 = div.find("h1")
            
            if h1 is None:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse view URL. 'h1' is None.")
                
                return viewUrl, False

            title = h1.text
            
            # Convert title to friendly URL and prepend category string.
            viewUrl = ConvertToUrl(title)
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.tag} P] Failed to parse view URL due to exception.")
            debugMsg(self.cfg, 0, e)
            
            return viewUrl, False
        
        return viewUrl, True
    
    def ParseBanner(self, url, resp):
        banner = None
        
        try:
            soup = BeautifulSoup(resp, "html.parser")
            
            # We need to find all li elements with carousel class.
            liEles = soup.findAll("li", class_="react-multi-carousel-item")
                        
            if liEles is None or len(liEles) < 1:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse banner. 'liEles' is None.")
                
                return banner, False
                        
            # Get first screenshot.
            imgEle = liEles[0].find("img")
            
            if imgEle is None:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse banner. 'imgEle' is None.")
                
                return banner, False
                        
            # Extract source image.
            imgSrc = imgEle.get("src")
            
            if not imgSrc.startswith("https") and not imgSrc.startswith("http"):
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse banner. Image source doesn't contain 'http' or 'https'.")
                
                return banner, False
                        
            # Get image contents.
            imgResp = requests.get(imgSrc)
            
            if imgResp.status_code == 200:
                imgContents = imgResp.content
            
                # Convert contents to base64.
                banner = base64.b64encode(imgContents).decode("utf-8")
            else:
                debugMsg(self.cfg, 1, f"[{self.tag} P] Banner image returned non-successful status code. Code => {imgResp.status_code}. Image => '{imgSrc}'.")
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.tag} P] Error to parse banner due to exception.")
            debugMsg(self.cfg, 0, e)
            
            return banner, False
        
        return banner, True
        
    def ParseName(self, url, resp):
        name = None
        
        try:
            soup = BeautifulSoup(resp, "html.parser")
            
            div = soup.find("div", class_="flex flex-wrap justify-center gap-4")
            
            if div is None:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse name. 'div' is None.")
                
                return name, False
            
            h1 = div.find("h1")
            
            if h1 is None:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse name. 'h1' is None.")
                
                return name, False
            
            name = h1.text
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.tag} P] Failed to parse name due to exception.")
            debugMsg(self.cfg, 0, e)
            
            return name, False
            
        return name, True
    
    def ParseOwnerName(self, url, resp):
        ownerName = None
        
        try:
            soup = BeautifulSoup(resp, "html.parser")
            
            div = soup.find("div", class_="flex flex-col gap-2")
            
            if div is None:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse owner name. 'div' is None.")
                
                return ownerName, False
            
            p = div.find("p")
                
            if p is None:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse owner name. 'p' is None.")
                
                return ownerName, False                   
                
            if "Maintained By" not in p.text:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse owner name. 'p' text doesn't contain 'Maintained By'.")
                
                return ownerName, False
            
            span = p.find("span", class_="font-bold")
            
            text = span.get_text()
            
            if text is None:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse owner name. 'text' is None.")
                
                return ownerName, False
            
            ownerName = text
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.tag} P] Failed to parse owner name due to exception.")
            debugMsg(self.cfg, 0, e)
            
            return ownerName, False
        
        return ownerName, True
    
    def ParseDescription(self, url, resp):
        description = None
        
        try:
            soup = BeautifulSoup(resp, "html.parser")
            
            div = soup.find("div", class_="markdown")
            
            if div is None:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse description. 'div' is None.")
                return description, False
            
            description = md(str(div))
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.tag} P] Failed to parse description due to exception.")
            debugMsg(self.cfg, 0, e)

            return description, False
        
        return description, True
    
    def ParseInstall(self, url, resp):
        install = None
        
        try:
            # We need to parse the /install page.
            self.driver.get(f"{url}/install")
            
            # Wait until H2 element with "Installation" is available.
            waitXpath = "//div[contains(@class, 'flex') and contains(@class, 'flex-col')]/h2[text() = 'Installation']"
            
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, waitXpath))
                )
            except Exception as e:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse install. Couldn't find 'h2' tag with 'Installation' text.")
                debugMsg(self.cfg, 4, e)
                
                return install, False
            
            soup  = BeautifulSoup(self.driver.page_source, "html.parser")
            
            div = soup.find("div", class_="markdown")
            
            if div is None:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse install. 'div' is None.")
                
                return install, False

            install = md(str(div))
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.tag} P] Failed to parse install due to exception.")
            debugMsg(self.cfg, 0, e)
            
            return install, False
            
        return install, True
    
    def ParseDownloads(self, url, resp):
        downloads = None
        
        try:
            # We need to parse the /downloads page.
            self.driver.get(f"{url}/downloads")
            
            # Wait until H2 element with "Downloads" is available.
            waitXpath = "//div[contains(@class, 'flex') and contains(@class, 'flex-col')]/h2[text() = 'Downloads']"
            
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, waitXpath))
                )
            except Exception as e:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse downloads. Couldn't find 'h2' tag with 'Downloads' text.")
                debugMsg(self.cfg, 4, e)
                
                return downloads, False
            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            
            # Retrieve all dividers with flex flex-col gap-2.
            divs = soup.find_all("div", class_="flex flex-col gap-2")
            
            if divs is None:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse downloads. 'divs' is None.")
                
                return downloads, False
            
            for div in divs:
                # Find h2.
                h2 = div.find("h2", recursive=False)
                
                if h2 is None or h2.text != "Downloads":
                    debugMsg(self.cfg, 5, f"[{self.tag} P] Found divider when parsing downloads that doesn't contain 'h2' element. Skipping this divider...")
                    
                    continue
                
                # Find all hrefs.
                a = div.findAll("a")
                
                if a is None:
                    debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse downloads. 'a' is None.")
                    continue
                
                downloads = []
                                    
                for dl in a:
                    try:
                        downloads.append({
                            "url": dl.get("href"),
                            "name": dl.text
                        })
                    except Exception as e:
                        debugMsg(self.cfg, 5, f"[{self.tag} P] Failed to parse specific download.")
                        debugMsg(self.cfg, 5, e)
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.tag} P] Failed to parse downloads due to exception.")
            debugMsg(self.cfg, 0, e)
            
            return downloads, False
            
        return downloads, True
    
    def ParseScreenshots(self, url, resp):
        screenshots = None
        
        try:                
            soup = BeautifulSoup(resp, "html.parser")
            
            # We need to find all li elements with carousel class.
            liEles = soup.findAll("li", class_="react-multi-carousel-item")
            
            if liEles is None:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse screenshots. 'liEles' is None.")
                
                return screenshots, False
            
            screenshots = []
            
            # Loop through each element.
            for liEle in liEles:
                # Now find the image inside of this.
                imgEle = liEle.find("img")
                
                if imgEle is None:
                    debugMsg(self.cfg, 5, f"[{self.tag} P] Failed to parse specific screenshot. 'imgEle' is None.")
                    
                    continue
                
                try:
                    # Retrieve our source.
                    src = imgEle.get("src")
                    
                    # Append to screenshots!
                    screenshots.append({
                        "url": str(src)
                    })
                except Exception as e:
                    debugMsg(self.cfg, 5, f"[{self.tag} P] Failed to parse specific download due to exception.")
                    debugMsg(self.cfg, 5, e)
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.tag} P] Failed to parse screenshots due to exception.")
            debugMsg(self.cfg, 0, e)
            
            return screenshots, False
        
        return screenshots, True
    
    def ParseInstallers(self, url, resp):
        installers = None
        
        try:
            # We need to wait for installer button with two-second timeout.
            btnXpath = "//button[contains(@class, 'btn-secondary')]"
            
            try:
                btn = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, btnXpath)))
            except Exception as e:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse installers. Unable to find clickable installers button.")
                debugMsg(self.cfg, 4, e)
                
                return installers, False
                
            if btn is None:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse installers. 'btn' is None.")
                
                return installers, False

            btn.click()
            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            
            # Retrieve install menu.
            divMenu = soup.find("div", class_="origin-top-right break-all absolute right-0 mt-2 w-44 min-w-full top-[100%] z-30 rounded-b p-2 bg-bestmods-3")
            
            if divMenu is None:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse installers. 'divMenu' is None.")
                
                return installers, False
            
            # Retrieve all link elements.
            aEles = divMenu.findAll("a")
            
            if aEles is None or len(aEles) < 1:
                debugMsg(self.cfg, 4, f"[{self.tag} P] Failed to parse installers. 'aEles' is either None or has 0 length.")
                
                return installers, False
            
            installers = []
            
            for a in aEles:
                link = a.get("href")
                
                if link is None:
                    debugMsg(self.cfg, 5, f"[{self.tag} P] Failed to parse specific installer. 'link' is None.")
                    
                    continue

                # Append to 
                installers.append({
                    "sourceUrl": self.url,
                    "url": link
                })
            
        except Exception as e:
            debugMsg(self.cfg, 0, f"[{self.url} P] Failed to parse installers due to exception.")
            debugMsg(self.cfg, 0, e)
            
            return installers, False
        
        return installers, True