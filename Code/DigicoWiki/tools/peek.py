#!/usr/bin/env python3
"""peek.py figures/NAME.png [width]  -> writes /tmp/peek-NAME.jpg downscaled (default 480px wide) for a cheap Read."""
import sys, os
from PIL import Image
src=sys.argv[1]; w=int(sys.argv[2]) if len(sys.argv)>2 else 480
im=Image.open(src).convert('RGB'); r=w/im.width; im=im.resize((w, max(1,int(im.height*r))))
out='/tmp/peek-'+os.path.basename(src).rsplit('.',1)[0]+'.jpg'; im.save(out, quality=55); print(out, im.size)
