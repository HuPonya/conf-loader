#!/usr/bin/env python
#


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import str

from future import standard_library

import os
import sys
import logging
import yaml
import jinja2

from jinja2.exceptions import UndefinedError

standard_library.install_aliases()

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


logging.basicConfig(level=debug_level,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    stream=sys.stdout,
                    name='conf-loader')


def _create_conf(tenv, config):
    # Use template file to create config
    logging.debug("Loading template %s", config['src'])
    template = tenv.get_template(config['src'])

    with open(config['dest'], 'w') as f:
        try:
            f.write(template.render(os.environ))
        except UndefinedError as err:
            logging.error("Can't parse template:%s, %s",
                          config['src'], err)
            sys.exit(1)

    logging.info("%s has been created successfully.", config['dest'])


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

    sys.exit(0)


if __name__ == '__main__':
    main()
