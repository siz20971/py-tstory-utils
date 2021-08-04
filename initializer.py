import settings
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from urllib import parse
import time

URL_AUTHORIZE = 'https://www.tistory.com/oauth/authorize?client_id={}&redirect_uri={}&response_type=code'
REST_GET_ACCESSCODE = 'https://www.tistory.com/oauth/access_token?client_id={}&client_secret={}&redirect_uri={}&code={}&grant_type=authorization_code'

def getAuthCode():
    uri = URL_AUTHORIZE.format(settings.app_id, settings.redirect_uri)
    
    # 1. Selenium으로 로그인
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("--log-level=3")
    options.add_argument("disable-gpu")
    options.add_argument("--window-size=800x600"); 

    driver = webdriver.Chrome(settings.driver_path, chrome_options = options)
    driver.set_window_position(0, 0)
    driver.set_window_size(1024, 768)

    driver.implicitly_wait(10) # 지정된 시간까지 기다림. Timeout.
    driver.get(uri)
    body = driver.find_element_by_css_selector('span')

    # 로그인 버튼 클릭
    time.sleep(1)
    driver.execute_script('kakaoAuth(true)')
    driver.implicitly_wait(10)

    # 폼 채우자
    login_form = driver.find_element_by_id('login-form')

    time.sleep(1)
    login_form.find_element_by_id('id_email_2').send_keys(settings.account_id)
    time.sleep(1)
    login_form.find_element_by_id('id_password_3').send_keys(settings.account_pw)
    time.sleep(1)
    login_btns = login_form.find_elements_by_class_name('btn_g')

        # 로그인 폼이 바뀔지도 모르겠으나, 
        # 우선 첫번째 버튼을 로그인 버튼이라고 가정하고 눌러버린다.
    if len(login_btns) > 0:
        login_btns[0].click()
    driver.implicitly_wait(10)

    # 2. 이후 데이터 받아오기
    time.sleep(1)
    driver.find_element_by_class_name('confirm').click()
    driver.implicitly_wait(10)

    parsedUrl = parse.urlparse(driver.current_url)
    queries = parse.parse_qs(parsedUrl.query)
    authCode = queries['code'][0]

    driver.close()

    return authCode

def getAccessCode(authCode):
    url = REST_GET_ACCESSCODE.format(settings.app_id, settings.secret_key, settings.redirect_uri, authCode)
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.replace('access_token=', '')
    else:
        return "Invalid"

print (" ### Start Authorize ### ")
authCode = getAuthCode()
print ("   AuthCode : " + authCode)

print (" ### Get AccessCode ### ")
accessCode = getAccessCode(authCode)
print ("   AccessCode : " + accessCode)


# AccessCode 테스트

# 1 Blog 정보
getInfoUrl = 'https://www.tistory.com/apis/blog/info?access_token={}&output=json'.format(accessCode)
response = requests.get(getInfoUrl)
infoJson = json.loads(response.content)
print (json.dumps(infoJson, indent=1))

firstBlogName = infoJson['tistory']['item']['blogs'][0]['name']

getListUrl = 'https://www.tistory.com/apis/post/list?access_token={}&output=json&blogName={}&page=1'.format(accessCode, firstBlogName)
response = requests.get(getListUrl)
print (json.loads(response.content))