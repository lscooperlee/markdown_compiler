import sys
import os
import argparse
from pathlib import Path

import pypandoc
from pypandoc.pandoc_download import download_pandoc

if __name__ == '__main__':

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

    nmspace = arg.parse_args()

    with open(nmspace.input) as input_file:
        #pdoc_args = ["-s", "--mathjax", "--highlight-style", "pygments", "--bibliography={0}".format(bibfile)]
        pdoc_args = ["-s", "--mathjax", "--highlight-style", "pygments"]
        html = pypandoc.convert_text(source=input_file.read(),
                                     format="markdown",
                                     to="html5",
                                     extra_args=pdoc_args)
    
    dirname, filename = os.path.split(nmspace.input)
    stem, _ = os.path.splitext(filename)
    if not nmspace.output:
        output_dir = os.path.join(dirname, f"{stem}_html")
    else:
        output_dir = nmspace.output

    Path(output_dir).mkdir(exist_ok=True)
    output_html_file = f"{stem}.html"
    output_file = os.path.join(output_dir, output_html_file)
    
    with open(output_file, 'w') as out_fd:
        out_fd.write(html)
    

