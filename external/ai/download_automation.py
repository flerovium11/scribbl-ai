import webbrowser
from time import sleep

chrome_path = 'C:/Programme/Google/Chrome/Application/chrome.exe %s'
# test_urls = ['http://docs.python.org/', 'https://www.google.com']
timeout = 0.1
url_prefix = 'https://storage.cloud.google.com/quickdraw_dataset/full/numpy_bitmap/'

with open('categories.txt', 'r') as categories_txt:
    urls = [url_prefix + category_name.replace(' ', '%20') + '.npy' for category_name in categories_txt.readlines()]

for url in urls[:50]:
    webbrowser.get(chrome_path).open(url)
    print('opened ' + url)
    sleep(timeout)
