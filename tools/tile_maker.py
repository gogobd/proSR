#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys

from PIL import Image


def crop_square(image, w0, h0, w1, h1):
    logger.debug(
        " Tile: {}x{}-{}x{}".format(
            w0, h0, w1, h1
        )
    )
    return image.crop((w0, h0, w1, h1))


def save_image(image, filename):
    directories = os.path.dirname(filename)
    if not os.path.isdir(directories):
        os.makedirs(directories)
    image.save(filename)
    logger.info(
        "Saved image {}.".format(
            repr(filename)
        )
    )


def save_all_squares(image, pattern_target, wr, hr):
    w, h = image.size

    logger.debug(
        "Image is {}x{} in {}x{} tiles.)".format(
            image.size[0],
            image.size[1],
            wr,
            hr,
        )
    )

    if (w < wr) or (h < hr):
        logger.warn("Image too small.")
        return

    wd = (wr - (w % wr)) / ( w // wr )
    hd = (hr - (h % hr)) / ( h // hr )

    i = 1
    for wn in range(w//wr + 1):
        for hn in range(h//hr + 1):
            logger.info("Tile {},{}".format(wn,hn))
            w0 = (wn * wr) - (wn * wd)
            h0 = (hn * hr) - (hn * hd)
            w1 = w0 + wr
            h1 = h0 + hr
            if w1 > w:
                logger.debug(
                    "Tile width is {}, but maximum is {}.".format(
                        w1,
                        w,
                    )
                )
                import pdb; pdb.set_trace()
            if h1 > h:
                logger.debug(
                    "Tile height is {}, but maximum is {}.".format(
                        h1,
                        h,
                    )
                )
                import pdb; pdb.set_trace()
            image_c = crop_square(
                image,
                w0,
                h0,
                w1,
                h1,
            )
            outputfile_name = pattern_target.format(i)
            i = i + 1
            save_image(image_c, outputfile_name)
            import pdb; pdb.set_trace()


def process_image(filename_source, filename_target):
    image = Image.open(filename_source)
    target_parts = os.path.splitext(filename_target)
    pattern_target = (
        target_parts[0] + 
        '-{:03d}' +
        target_parts[1]
    )
    save_all_squares(
        image,
        pattern_target,
        args['size'],
        args['size'],
    )


def configuration_override(
    configuration_file,
    params,
    keys=[
        'source_dir',
        'target_dir',
        'size',
    ],
    one_time=False,
):
    """Override keys in configuration with values from a json file."""
    if os.path.isfile(configuration_file):
        new_config = json.loads(open(configuration_file, 'r').read())
        for key, value in new_config.items():
            if key in keys:
                logger.debug(
                    "File {} key {} changed from {} to {}".format(
                        repr(configuration_file),
                        repr(key),
                        repr(params[key]),
                        repr(value),
                    )
                )
                params[key] = value
            else:
                logger.warn(
                    "File {} key {} does not exist (value={}).".format(
                        repr(configuration_file),
                        repr(key),
                        repr(value),
                    )
                )
        if one_time:
            move_file(configuration_file, configuration_file + '.done')
    else:
        logging.debug(
            "File {} not seen, skipping.".format(
                repr(configuration_file)
            )
        )
    return params


parser = argparse.ArgumentParser(
    description='Create square tiles from images'
)
parser.add_argument(
    "source_dir",
    help="Path to source video tree root",
    nargs='?',
    default='.',
)
parser.add_argument(
    "target_dir",
    help="Üath to target video tree root",
    nargs='?',
    default='./converted/',
)
parser.add_argument(
    'size',
    metavar='N',
    type=int,
    nargs='?',
    help='Target size for squares',
    default = 512,
)
parser.add_argument(
    "--config_file",
    help="Path and filename for a config file",
    default=os.path.splitext(sys.argv[0])[0] + '.cfg',
)
parser.add_argument(
    "--loglevel",
    help="Level of verbosity",
    default=logging.DEBUG,
)
parser.add_argument(
    "--source_extensions",
    help="Image file extensions separated by comma",
    default=','.join(
        [
            i[1:] for i in Image.registered_extensions().keys()
        ],
    )
)
parser.add_argument(
    "--target_extension",
    help="target file extension",
    default='.png',
)
args = parser.parse_args()
args = dict(args._get_kwargs())
args = configuration_override(
    args['config_file'],
    args,
    keys=args.keys(),
    one_time=False
)

if not args['target_extension'].startswith('.'):
    args['target_extension'] = '.' + args['target_extension']
source_extensions = []

for source_extension in args['source_extensions'].split(','):
    if source_extension.startswith('.'):
        source_extensions.append(source_extension)
    else:
        source_extensions.append('.' + source_extension)
args['source_extensions'] = source_extensions
del source_extensions

logging.basicConfig(
    format='%(asctime)s [%(process)s] %(levelname)s %(pathname)s:%(lineno)s: %(message)s',  # NOQA E501
    # filename=os.path.splitext(sys.argv[0])[0]+'.log',
    # level=logging.INFO,
    level=args['loglevel'],
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)
logger.setLevel(args['loglevel'])     # workaround
logger.debug(args)

for root, subdirList, fileList in os.walk(args['source_dir'], topdown=False):
    imagenames = []
    for filename in fileList:
        if os.path.splitext(filename)[1].lower() in args['source_extensions']:
            imagenames.append(filename)
    if imagenames:
        print(
            '{root}: {nimg}/{nfiles} images.'.format(
                root=root,
                nimg=len(imagenames),
                nfiles=len(fileList),
            )
        )
        for imagename in imagenames:
            inputfile_name = os.path.join(root, imagename)
            logging.info(
                "Processing file {}".format(
                    repr(inputfile_name)
                )
            )
            directories = ''
            if root.startswith(args['source_dir']):
                directories = root[len(args['source_dir'])+1:]
            outputfile_directories = os.path.join(
                args['target_dir'],
                directories,
            )
            outputfile_name = os.path.join(
                outputfile_directories,
                os.path.splitext(imagename)[0] + args['target_extension']
            )
            logger.debug(
                "{source} -> {target}".format(
                        source=inputfile_name,
                        target=outputfile_name,
                    )
            )
            process_image(
                inputfile_name,
                outputfile_name,
            )
