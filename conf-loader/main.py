#!/usr/bin/env python
#

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import str
from builtins import bytes

from future import standard_library

import os
import sys
import logging
import yaml
import requests
import jinja2

from jinja2.exceptions import UndefinedError

standard_library.install_aliases()
# Enable verified HTTPS requests on older Pythons
# http://urllib3.readthedocs.org/en/latest/security.html
if sys.version_info[0] == 2:
    requests.packages.urllib3.contrib.pyopenssl.inject_into_urllib3()
    from urllib import quote
    from urllib import urlencode
else:
    from urllib.parse import quote
    from urllib.parse import urlencode

BASE_DIR = os.getcwd()

with open("%s/.ci/config/config.yml" % BASE_DIR, 'r') as f:
    try:
        DATA = yaml.load(f)
    except yaml.YAMLError as exc:
        print(exc)
        sys.exit(1)

if os.environ.get('confloader_debug'):
    if os.environ['confloader_debug']:
        debug_level = logging.DEBUG
    else:
        debug_level = logging.INFO
else:
    if DATA['debug']:
        debug_level = logging.DEBUG
    else:
        debug_level = logging.INFO

if DATA.get('gitlab_token'):
    GITLAB_HEADERS = {'PRIVATE-TOKEN': DATA['gitlab_token']}
    GITLAB_BASEURL = DATA['gitlab_baseurl']
else:
    GITLAB_HEADERS = None

REQUESET_TIMEOUT = 20

logging.basicConfig(level=debug_level,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    stream=sys.stdout,
                    name='conf-loader')


def _create_conf(tenv, config):
    # Use system environ and template file to create config
    logging.debug("Loading template %s", config['src'])
    template = tenv.get_template(config['src'])

    with open(config['dest'], 'wb') as f:
        try:
            out = bytes(template.render(os.environ), "utf-8")
            f.write(out)
        except UndefinedError as err:
            logging.error("Can't parse template:%s, %s",
                          config['src'], err)
            sys.exit(1)

    logging.info("%s from template has been created successfully.",
                 config['dest'])


def _gitlab_conf(config):
    # Download gitlab files with token
    # https://gitlab.com/<group_name>/<project_name>/raw/master/<f??older>/<file_name>?p??rivate_token=<your_key>
    logging.debug("Loading gitlab files %s", config['name'])
    with open(config['dest'], 'wb') as handle:
        url = "%s/%s" % (GITLAB_BASEURL, os.environ[config['name']])
        response = requests.get(url, headers=GITLAB_HEADERS,
                                timeout=REQUESET_TIMEOUT, stream=True,
                                allow_redirects=False)

        if response.status_code != 200:
            raise RuntimeError("Cant load gitlab files", response.text)

        for block in response.iter_content(1024):
            handle.write(block)

    logging.info("%s from gitlab has been created successfully.",
                 config['dest'])


def main():
    logging.info("Starting create conf...")
    logging.debug(os.environ)

    templateLoader = jinja2.FileSystemLoader(searchpath="%s/.ci/config/" %
                                             BASE_DIR)
    templateEnv = jinja2.Environment(loader=templateLoader,
                                     undefined=jinja2.StrictUndefined)

    for config in DATA['configs']:
        if config['type'] == 'tpl':
            _create_conf(templateEnv, config)
        elif config['type'] == 'gitlab':
            _gitlab_conf(config)

    sys.exit(0)


if __name__ == '__main__':
    main()
