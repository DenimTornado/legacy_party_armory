"""Derive a numeric UV selection mask from the stock sword mesh, without repainting its textures."""
from pathlib import Path
import xml.etree.ElementTree as E
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parent
def build():
 r=E.parse(ROOT/'carsomyr.dae');ns={'c':'http://www.collada.org/2005/11/COLLADASchema'}
 mesh=r.find('.//c:geometry/c:mesh',ns)
 sources={s.get('id'):np.fromstring(s.find('c:float_array',ns).text,sep=' ').reshape(-1,int(s.find('c:technique_common/c:accessor',ns).get('stride'))) for s in mesh.findall('c:source',ns)}
 tri=mesh.find('c:triangles',ns);inputs={i.get('semantic'):(int(i.get('offset')),i.get('source')[1:]) for i in tri.findall('c:input',ns)}
 indices=np.fromstring(tri.find('c:p',ns).text,sep=' ',dtype=int).reshape(-1,max(i[0] for i in inputs.values())+1).reshape(-1,3,max(i[0] for i in inputs.values())+1)
 pos=sources[inputs['VERTEX'][1]][indices[:,:,inputs['VERTEX'][0]]]
 uv=sources[inputs['TEXCOORD'][1]][indices[:,:,inputs['TEXCOORD'][0]]]
 centers=pos.mean(axis=1)
 selected=(centers[:,2]>-.058)&(centers[:,2]<.24)&(np.abs(centers[:,0])<.035)
 mask=Image.new('L',(1024,1024),0);draw=ImageDraw.Draw(mask)
 for coords in uv[selected]:draw.polygon([(float(u)*1023,(1-float(v))*1023) for u,v in coords],fill=255)
 # Pad only two pixels into the UV gutter to avoid a pale seam at mip boundaries.
 mask=mask.filter(ImageFilter.MaxFilter(5))
 rgba=Image.merge('RGBA',(mask,mask,mask,Image.new('L',mask.size,255)))
 rgba.save(ROOT/'carsomyr_grip_mask.dds');mask.save(ROOT/'carsomyr_grip_mask.png')
 # A generated shader lookup table, not an edit of native weapon textures.
 # Every row is equivalent: native gradient indexing cannot select another hue.
 t=np.linspace(0,1,256);red=np.clip(np.stack([.12+.88*t,.006+.075*t,.003+.02*t],axis=-1)*255,0,255).astype('uint8')
 lut=np.tile(red[None,:,:],(256,1,1));Image.fromarray(lut).convert('RGBA').save(ROOT/'dragon_red_gradient.dds')
 # Geometry diagnostic: selected triangles red, untouched blade/guard silver.
 diagram=Image.new('RGB',(400,1100),(24,26,30));pen=ImageDraw.Draw(diagram)
 for polygon,isgrip in zip(pos,selected):
  pen.polygon([(200+float(x)*500,(float(z)+1.6)*500+20) for x,y,z in polygon],fill=(220,28,16) if isgrip else (170,180,194))
 diagram.save(ROOT/'carsomyr_grip_selection.png')
 assert 100<selected.sum()<1000,int(selected.sum())
 print('Grip triangles selected:',int(selected.sum()),'/',len(selected))
if __name__=='__main__':build()
