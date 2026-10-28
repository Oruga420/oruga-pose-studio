#!/usr/bin/env python3
"""Pack only fully rendered poses into compact WebP strips and a static index."""
import argparse,json,math
from pathlib import Path
from PIL import Image
BASE=Path(__file__).resolve().parents[1]
ANGLES=['front','three-quarter','side','back','high']
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--catalog',default=str(BASE/'poses/catalog.json'));ap.add_argument('--renders',default=str(BASE/'assets'));ap.add_argument('--output',default=str(BASE/'site-assets'));ap.add_argument('--width',type=int,default=600);ap.add_argument('--height',type=int,default=750);args=ap.parse_args()
    source=json.loads(Path(args.catalog).read_text());poses=source['poses'] if isinstance(source,dict) else source
    out=Path(args.output);(out/'plates').mkdir(parents=True,exist_ok=True);(out/'thumbs').mkdir(exist_ok=True)
    ready=[];missing=[];thumbs=[];plate=None
    for p in poses:
        paths=[Path(args.renders)/p['id']/f'{a}.png' for a in ANGLES]
        if not all(x.exists() for x in paths):missing.append(p['id']);continue
        strip=Image.new('RGB',(args.width*5,args.height))
        for i,path in enumerate(paths):
            with Image.open(path) as im:strip.paste(im.convert('RGB').resize((args.width,args.height),Image.Resampling.LANCZOS),(i*args.width,0))
        plate_index=len(ready)//10;plate_row=len(ready)%10
        if plate_row==0:plate=Image.new('RGB',(args.width*5,args.height*10),(210,211,208))
        plate.paste(strip,(0,plate_row*args.height))
        if plate_row==9:plate.save(out/'plates'/f'{plate_index:03d}.webp','WEBP',lossless=True,method=6)
        thumbs.append(strip.crop((args.width,0,args.width*2,args.height)).resize((160,200),Image.Resampling.LANCZOS))
        metadata=Path(args.renders)/p['id']/'metadata.json'
        info=json.loads(metadata.read_text()) if metadata.exists() else p
        ready.append({**p,'sprite':f'site-assets/plates/{plate_index:03d}.webp','spriteRows':10,'spriteRow':plate_row,'width':args.width,'height':args.height,'warnings':info.get('warnings',[]),'thumb':{'sheet':len(ready)//100,'index':len(ready)%100}})
    if ready and len(ready)%10:plate.save(out/'plates'/f'{(len(ready)-1)//10:03d}.webp','WEBP',lossless=True,method=6)
    for start in range(0,len(thumbs),100):
        batch=thumbs[start:start+100];sheet=Image.new('RGB',(1600,2000),(220,222,218))
        for i,im in enumerate(batch):sheet.paste(im,((i%10)*160,(i//10)*200))
        sheet.save(out/'thumbs'/f'{start//100:03d}.webp','WEBP',quality=85,method=6)
    result={'title':'Oruga Pose Studio','version':'1.0','license':'CC0-1.0','angles':ANGLES,'renderedCount':len(ready),'catalogCount':len(poses),'missingCount':len(missing),'poses':ready}
    (BASE/'gallery-data.js').write_text('window.POSE_DATA = '+json.dumps(result,ensure_ascii=False,separators=(',',':'))+';\n')
    (BASE/'poses/gallery-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    (BASE/'poses/render-status.json').write_text(json.dumps({'rendered':len(ready),'catalog':len(poses),'missing':missing},indent=2))
    print(f'{len(ready)} ready poses; {len(ready)*5} views; {len(missing)} not published (incomplete).')
if __name__=='__main__':main()
