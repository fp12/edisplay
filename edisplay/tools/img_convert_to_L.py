import os, sys
from PIL import Image

for infile in sys.argv[1:]:
    f, e = os.path.splitext(infile)
    outfile = f + '_l.jpg'
    if infile != outfile:
        try:
            with Image.open(infile) as im:
                img_grayscale = im.convert('L')
                img_grayscale.save(outfile)
        except OSError as e:
            print(f'cannot convert {infile}: {e}')