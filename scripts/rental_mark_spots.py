"""Project world ground points using measured horizontal FOV; no manual image placement."""
import os,json,math,argparse
from PIL import Image,ImageDraw,ImageFont
P=argparse.ArgumentParser();P.add_argument('spots_dir');P.add_argument('--points',required=True);a=P.parse_args()
points=json.load(open(a.points,encoding='utf-8'));views=json.load(open(os.path.join(a.spots_dir,'rental_wide_meta.json'),encoding='utf-8'))
def sub(a,b):return [a[i]-b[i] for i in range(3)]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def norm(v):d=math.sqrt(dot(v,v));return [x/d for x in v]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',29);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for view in views:
 im=Image.open(view['file']).convert('RGB');d=ImageDraw.Draw(im);w,h=im.size;c=view['pos'];f=norm(sub(view['target'],c));right=norm(cross(f,[0,0,1])) if abs(f[2])<.9999 else [1,0,0];up=cross(right,f)
 px=w/(2*math.tan(math.radians(float(view['GetAngleOfView']))/2));results=[]
 if view['id']=='6':
  # The complete merged building was hidden, not just the roof.
  footprint=[]
  for wp in [[-4825,-3089,79],[-3506,-3089,79],[-3506,-1840,79],[-4825,-1840,79]]:
   v=sub(wp,c);depth=dot(v,f);footprint.append((w/2+px*dot(v,right)/depth,h/2-px*dot(v,up)/depth))
  d.line(footprint+[footprint[0]],fill='#ff8877',width=4)
  d.text((footprint[0][0]+10,footprint[0][1]-32),'MERGED BUILDING HIDDEN - NOT AN EMPTY LOT',font=small,fill='#ff8877')
 allowed={'1':'EF','2':'D','3':'','4':'ABC','5':'EF','6':'ABCDEF'}
 for p in points:
  if p['id'] not in allowed[view['id']]:continue
  v=sub(p['pos'],c);depth=dot(v,f)
  if depth<=0:continue
  x=w/2+px*dot(v,right)/depth;y=h/2-px*dot(v,up)/depth
  if 15<x<w-15 and 15<y<h-15:
   d.ellipse((x-9,y-9,x+9,y+9),fill='#ffd33d',outline='black',width=3)
   txt=p['id'];box=d.textbbox((x+13,y-31),txt,font=font);d.rectangle((box[0]-5,box[1]-4,box[2]+5,box[3]+4),fill='black');d.text((x+13,y-31),txt,font=font,fill='#ffe66d')
   results.append([p['id'],round(x,2),round(y,2)])
 d.rectangle((12,12,540,51),fill='black');d.text((22,20),'GROUND SPOTS | WIDE '+view['id']+' | XY in cm',font=small,fill='white')
 im.save(view['file'].replace('.png','_marked.png'))
 view['projected_spots']=results
json.dump(views,open(os.path.join(a.spots_dir,'rental_projection.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=2)
