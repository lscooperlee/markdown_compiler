import sys
import re
import os
import argparse
import base64
import subprocess
import tempfile
from pathlib import Path

import pypandoc
from pypandoc.pandoc_download import download_pandoc


def python_file_handler(content, filename, base_dir, output_dir):
    return content


def image_handler(content, filename, base_dir, output_dir):
    def image_to_base64(image_data):
        image_64_encode = base64.standard_b64encode(image_data)
        image_string = image_64_encode.decode()
        image_string = 'data:image/png;base64,' + image_string
        return image_string

    name = filename if os.path.isabs(filename) else os.path.join(
        base_dir, filename)
    print(name)
    try:
        with open(name, 'rb') as fd:
            encoded = image_to_base64(fd.read())
            content = content.replace(filename, encoded, 1)
    except FileNotFoundError:
        print(f"{name} not exist")

    return content


def drawio_handler(content, filename, base_dir, output_dir):
    with tempfile.TemporaryDirectory() as tmp_dir:
        extract_name = os.path.join(tmp_dir, 'a.png')
        name = filename if os.path.isabs(filename) else os.path.join(
            base_dir, filename)
        subprocess.call(['drawio', '-x', '-o', extract_name, name])
        return image_handler(content.replace(filename, extract_name, 1),
                             extract_name, base_dir, output_dir)


content_handler = {
    "py": python_file_handler,
    "drawio": drawio_handler,
    "jpg": image_handler,
    "png": image_handler,
}


def main():
    target_path = os.path.dirname(sys.executable)
    pandoc_path = os.path.join(target_path, 'pandoc')

    if not os.path.exists(os.path.join(target_path, 'pandoc')):
        try:
            download_pandoc(targetfolder=target_path,
                            download_folder='/tmp',
                            delete_installer=True)
        except FileNotFoundError:  # https://github.com/bebraw/pypandoc/issues/200
            pass

    arg = argparse.ArgumentParser()

    arg.add_argument("-i", "--input", nargs='?', required=True)
    arg.add_argument("-o", "--output", nargs='?', default=None)
    arg.add_argument("-f", "--format", nargs='?', type=str, default='html')

    nmspace = arg.parse_args()

    dirname, filename = os.path.split(nmspace.input)
    stem, _ = os.path.splitext(filename)
    if not nmspace.output:
        output_dir = os.path.join(dirname, f"{stem}_{nmspace.format}")
    else:
        output_dir = nmspace.output

    Path(output_dir).mkdir(exist_ok=True)
    output_html_file = f"{stem}.{nmspace.format}"
    output_file = os.path.join(output_dir, output_html_file)

    with open(nmspace.input) as input_file:
        content = input_file.read()

    p = re.compile(r'!\[(?P<id>.*)\]\((?P<url>.*?)(\)|\s+.*\))')
    ret = p.finditer(content)
    for m in ret:
        matched = m.groupdict()
        ext = matched['url'].split('.')[-1]
        if ext in content_handler:
            content = content_handler[ext](content, matched['url'], dirname,
                                           output_dir)

    #pdoc_args = ["-s", "--mathjax", "--highlight-style", "pygments", "--bibliography={0}".format(bibfile)]
    pdoc_args = ["-s", "--mathjax", "--highlight-style", "pygments"]
    html = pypandoc.convert_text(source=content,
                                 format="markdown",
                                 to=nmspace.format,
                                 outputfile=output_file,
                                 extra_args=pdoc_args)


if __name__ == '__main__':
    main()