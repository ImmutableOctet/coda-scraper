import urllib.request
from urllib.parse import urlparse

import os
import re
import errno
import argparse

# from html.parser import HTMLParser
from lxml import html
import requests

def ensure_path(path):
	if not os.path.exists(os.path.dirname(path)):
		try:
			os.makedirs(os.path.dirname(path))
		except OSError as exc:
			if exc.errno != errno.EEXIST:
				raise


def clean_filename(path, unknown_symbol='_'):
    return re.sub('[^\w\-_\. ]', unknown_symbol, path)


def main(argv):
    from argparse import RawTextHelpFormatter

    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, description='')

    parser.add_argument("-out", dest='output_path', help='')
    parser.add_argument("-input", dest='blog_url', help='', default='https://coda.s3m.us/blog')
    parser.add_argument("-begin", dest='begin', help='', default=1)
    parser.add_argument("-end", dest='end', help='', default=58)

    cfg = parser.parse_args(argv)

    if (not cfg.output_path):
        print('Output path missing, outputting links instead:\n')

    for page_index in range(cfg.begin, cfg.end):
        page_url = f'{cfg.blog_url}/page/{page_index}'
        page = requests.get(page_url)
        page_content = page.content

        tree = html.fromstring(page_content)

        #print(page_content)

        articles = tree.xpath("/html/body/div[@id='page']/div[@id='content']/section[@id='primary']/main/article")

        for post in articles:
            post_links = post.xpath("div/p/a")

            for link_entry in post_links:
                link = link_entry.attrib['href']

                if (link.endswith(".mp3") or link.endswith(".ogg") or link.endswith(".m4a") or link.endswith(".wav") or link.endswith(".wma")):
                    if (cfg.output_path):
                        try:
                            download_url = urlparse(link)
                            download_filename = clean_filename(os.path.basename(download_url.path))

                            file_output_path = os.path.join(cfg.output_path, download_filename)

                            if (os.path.exists(file_output_path)):
                                print(f"Existing file found at: \"{file_output_path}\", skipping download of \"{link}\".")
                            else:
                                print(f"Downloading file: \"{link}\" to \"{file_output_path}\"...")

                                ensure_path(file_output_path)

                                urllib.request.urlretrieve(link, file_output_path) # url_parsed
                        except:
                            print(f'Download failed for: \"{link}\", continuing anyway...')

                        pass
                    else:
                        print(link)


if (__name__ == '__main__'):
    #main(['-out', 'E:\\Downloads\\Coda Music Archive'])
    main(sys.argv[1:])
