import svgwrite
import json
import randomcolor

rand_color = randomcolor.RandomColor()

import colors

with open('segments.json') as f:
    data = json.load(f)


for layer, segments in data.iteritems():
    print layer
    dwg = svgwrite.Drawing('layer-{}.svg'.format(layer), profile='tiny')
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill='rgb(10,10,10)'))
    for segment in segments:
        r, g, b = rand_color.generate(format_='Array,rgb')[0]
        elements = segment['e']
        for x, y, w, h in elements:
            x /= 500.0
            y /= 500.0
            w /= 500.0
            h /= 500.0
            dwg.add(dwg.rect((100+x, 100+(400000/500.0)-y-(h)), (w, h), fill=svgwrite.rgb(r, g, b)))
    dwg.save()

