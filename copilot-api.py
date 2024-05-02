import os
import time
import requests
import json
import time
from urllib.parse import urlparse
from seleniumwire import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions

cookies = json.load(open("cookies.json")) # Use editthiscookie to export the cookies

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.headless = True

url = "https://www.bing.com/chat?q=Microsoft+Copilot&FORM=hpcodx"
wd = webdriver.Chrome(options=chrome_options)
wd.get(url)
for cookie in cookies: 
    try:
      wd.add_cookie({"domain":str(cookie["domain"]),"name":str(cookie["name"]),"value":str(cookie["value"])})
    except exceptions.InvalidCookieDomainException as e:
      print(e )
wd.get(url)
time.sleep(1)
question = input("You: ")
elem = wd.switch_to.active_element
elem.send_keys(question)
elem.send_keys(Keys.RETURN)

tStart = time.time()
gotEm = False
while not gotEm: 
  if time.time() - tStart > 50:
    break

  cib_serp_main_el = wd.find_element(by=By.CLASS_NAME, value="cib-serp-main")
  cib_serp_main_root = wd.execute_script('return arguments[0].shadowRoot', cib_serp_main_el)
  cib_conv_main_root = wd.execute_script('return arguments[0].getElementById("cib-conversation-main").shadowRoot', cib_serp_main_root)
  cib_chat_main_el = wd.execute_script('return arguments[0].getElementById("cib-chat-main")', cib_conv_main_root)
  cib_chat_turns =  wd.execute_script('return arguments[0].querySelectorAll("cib-chat-turn")', cib_chat_main_el)
  cib_chat_turn = cib_chat_turns[-1]
  cib_chat_turn_root = wd.execute_script('return arguments[0].shadowRoot', cib_chat_turn)
  cib_message_groups = wd.execute_script('return arguments[0].querySelectorAll("cib-message-group")', cib_chat_turn_root)
  if len(cib_message_groups) % 2 != 0:
    continue
  cib_message_group = cib_message_groups[-1]
  cib_message_group_root = wd.execute_script('return arguments[0].shadowRoot', cib_message_group)
  cib_message_sections = wd.execute_script('return arguments[0].querySelectorAll("cib-message")', cib_message_group_root)
  for section in cib_message_sections:
    sectionRoot = wd.execute_script('return arguments[0].shadowRoot', section)
    content = wd.execute_script('return arguments[0].querySelector(".content")', sectionRoot)
    txt = content.get_attribute("aria-label")
    oldLen = len(txt)
    time.sleep(1)
    while len(content.get_attribute("aria-label")) != oldLen:
      oldLen = len(txt)
      txt = content.get_attribute("aria-label")
      time.sleep(1)
    
    if content:
      print("Copilot: ", txt )
      gotEm = True

height = wd.execute_script('return document.documentElement.scrollHeight')
width  = wd.execute_script('return document.documentElement.scrollWidth')
wd.set_window_size(width, height)  # the trick
wd.save_screenshot("screenie.png")

wd.quit()
