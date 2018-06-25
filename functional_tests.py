from selenium import webdriver
from selenium.webdriver import FirefoxOptions

# need to add headless option because we are testing in a vm without gui.
opts = FirefoxOptions()
opts.add_argument("--headless")
browser = webdriver.Firefox(firefox_options=opts)
browser.get('http://localhost:8000')

# Check to see if Sébastien's title page is rendering properly.
assert 'Sébastien' in browser.title
