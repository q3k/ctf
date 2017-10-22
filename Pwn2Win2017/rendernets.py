import svgwrite
import json
import randomcolor

rand_color = randomcolor.RandomColor()

import colors

with open('nets.json') as f:
    data = json.load(f)


dwg = svgwrite.Drawing('nets.svg', profile='tiny')
for net in data:
    print net['e']
    r, g, b = rand_color.generate(format_='Array,rgb')[0]
    for x, y, w, h in net['e']:
       x /= 500.0
       y /= 500.0
       w /= 500.0
       h /= 500.0
       dwg.add(dwg.rect((100+x, 100+(400000/500.0)-y-(h)), (w, h), fill=svgwrite.rgb(r, g, b)))
dwg.save()

