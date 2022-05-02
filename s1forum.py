import re
from tkinter.tix import Tree
import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs, NavigableString, Tag
from urllib.parse import urlparse,parse_qs
from qqbot.model.message import MessageEmbedField, MessageEmbed


class S1Forum:
    # proxies = {
    #     'http': 'http://127.0.0.1:1080',
    #     'https': 'https://127.0.0.1:1080'
    # }

    def __init__(self, hostname, username, password, questionid='0', answer=None, proxies=None):
        self.session = aiohttp.ClientSession() 
        if hostname is None:
            hostname = "bbs.saraba1st.com/2b"
        self.hostname = hostname
        self.username = username
        self.password = password
        self.questionid = questionid
        self.answer = answer
        if proxies:
            self.proxies = proxies

    @classmethod
    async def user_login(cls, hostname, username, password, questionid='0', answer=None, proxies=None):
        user = S1Forum(hostname, username, password, questionid, answer, proxies)
        await user.login()

    def checkauth(self):
        cookies = self.session.cookie_jar.filter_cookies(f"https://{self.hostname}")
        if 'B7Y9_2132_auth' in cookies:
            # print(f'Welcome {self._username}!')
            return True
        else:
            # print("Auth failed")
            return False

    async def fetchAndParse(self,url:str):
        if not self.checkauth():
            await self.login()
        async with self.session.get(url) as resp:
            if resp.status != 200:
                return "no data"
            resptext = await resp.text()
        soup = bs(resptext,'html.parser')
        postContent = soup.find(id="content")
        return postContent

    async def getlist(self,url:str,board:str):
        post = await self.fetchAndParse(url)
        if type(post) != NavigableString and type(post) != Tag:
            return post
        embed = MessageEmbed()
        embed.title = board
        embed.prompt = board + "新帖列表"
        embed.fields = []
        i = 0
        for s in post.find_all('ul')[1].find_all('a'):
            i += 1
            s = str(i)+"."+s.string
            # qqbot.logger.info(s)
            # await asyncio.sleep(0.1)
            if len(s) >= 50:
                s = s[0:50] + "..."
            if i > 15:
                break
            else:
                embed.fields.append(MessageEmbedField(name=s, value="content")) 
        return embed


    async def getpost(self,link:str):
        tid = link
        if tid.startswith(f"https://{self.hostname}/"):
            urlraw =urlparse(link)
            if "&tid=" in tid:
                tid = parse_qs(urlraw.query)["tid"][0]
            else:
                tid = urlraw.path[11:-9]
        
        url = f'https://{self.hostname}/archiver/tid-{tid}.html'
        
        post = await self.fetchAndParse(url)

        if type(post) != NavigableString and type(post) != Tag:
            return post
        # 构造消息发送请求数据对象
        embed = MessageEmbed()
        embed.title = post.h3.string
        embed.prompt = post.p.string
        embed.fields = []
        for s in post.stripped_strings:
            # qqbot.logger.info(s)
            # await asyncio.sleep(0.1)
            if len(s) >=50:
                s = s[0:50] + "..."
            if len(embed.fields) > 15:
                break
            else:
                embed.fields.append(MessageEmbedField(name=s, value="content")) 
        return embed

    def close(self):
        if self.session is not None:
            self.session.close()

    async def fetch(self):
        async with self.session.get(f'https://{self.hostname}/member.php?mod=logging&action=login') as resp:
            assert resp.status == 200
            return await resp.text()

    async def form_hash(self):
        rst = await self.fetch()
        loginhash = re.search(r'<div id="main_messaqge_(.+?)">', rst).group(1)
        formhash = re.search(r'<input type="hidden" name="formhash" value="(.+?)" />', rst).group(1)
        return loginhash, formhash

    async def login(self):
        loginhash, formhash = await self.form_hash()
        login_url = f'https://{self.hostname}/member.php?mod=logging&action=login&loginsubmit=yes&loginhash={loginhash}&inajax=1'
        formData = {
            'formhash': formhash,
            'referer': f'https://{self.hostname}/',
            'loginfield': self.username,
            'username': self.username,
            'password': self.password,
            'questionid': self.questionid,
            'answer': self.answer,
            'cookietime': 2592000
        }
        # login_rst = self.session.post(login_url, proxies=self.proxies, data=formData)
        # login_rst = await self._session.post(login_url, data=formData)
        
        # self._session.post(login_url, data=formData)
        async with self.session.post(login_url, data=formData) as resp:
            assert resp.status == 200
            resptext = await resp.text()
        # cookies =  self._session.cookie_jar.filter_cookies('https://bbs.saraba1st.com/2b')
        if self.checkauth():
            print(f'Welcome {self.username}!')
            return True
        else:
            print("Auth failed")
            return False
        # if 'B7Y9_2132_auth' in cookies:
        #     print(f'Welcome {self._username}!')
        #     # return True
        # else:
        #     print("Auth failed")
        #     # return False
        #     # raise ValueError('Verify Failed! Check your username and password!')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(S1Forum.user_login("bbs.saraba1st.com/2b","username","password"))
