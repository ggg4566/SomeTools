#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:flystart
# home:www.flystart.org
# time:2022/9/15

from flask import Flask
from flask import request

import asyncio
from pyppeteer import launch


url = 'https://passport.fang.com/'
app = Flask(__name__)

proxy = ''
gpage=None
main_loop = None


async def login():
    ret = ""
    global gpage

    browser = await launch(headless=False, args=['--disable-infobars', '--proxy-server=' + proxy])
    page = await browser.newPage()
    gpage = page
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36')
    await page.evaluateOnNewDocument('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
    await page.goto(url)

    try:
        con = await page.content()
        # print(con)
        foo = await page.evaluate("""
        {
          encryptedString(key_to_encode,"test")

        }
        """)
        print(foo)
        ret = foo
    except Exception as e:
        print(e)
    # await browser.close()
    return ret


async def get_calc_hash(page,val):
    ret = ""
    try:
        foo = await page.evaluate("""
           {
             encryptedString(key_to_encode,'%s')

           }
           """%val)
        print(foo)
        ret = foo
    except Exception as e:
        print(e)
    return ret


def start_load():
    loop = asyncio.get_event_loop()
    global main_loop
    main_loop  = loop
    res = loop.run_until_complete(asyncio.gather(login()))
    print(res)
    print("load success!")


@app.route('/')
def index():
    global gpage
    payload = request.args.get("payload")
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    rst = main_loop.run_until_complete(get_calc_hash(gpage,payload))
    calc_hash = rst
    return calc_hash


if __name__ == "__main__":
    start_load()
    app.run()
