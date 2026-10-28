import json,math,re,unittest
from pathlib import Path
from PIL import Image
BASE=Path(__file__).resolve().parents[1]
class ProjectTests(unittest.TestCase):
    def test_seed_catalog(self):
        data=json.loads((BASE/'poses/seed-24.json').read_text());poses=data['poses']
        self.assertEqual(len(poses),24);self.assertEqual(len({p['id'] for p in poses}),24)
        for p in poses:
            self.assertTrue(re.fullmatch(r'[A-Za-z0-9_-]+',p['id']))
            for field in ['root','torso_euler','head_euler']:
                self.assertEqual(len(p[field]),3)
                self.assertTrue(all(isinstance(x,(int,float)) and math.isfinite(x) for x in p[field]))
            for field in ['wrists','elbows','ankles','knees']:
                for side in ['L','R']:
                    self.assertEqual(len(p[field][side]),3)
                    self.assertTrue(all(math.isfinite(x) for x in p[field][side]))
    def test_published_manifest(self):
        path=BASE/'poses/gallery-manifest.json'
        self.assertTrue(path.exists(),'Run pack_gallery.py first')
        data=json.loads(path.read_text());poses=data['poses']
        self.assertEqual(data['renderedCount'],len(poses));self.assertEqual(len({p['id'] for p in poses}),len(poses))
        self.assertEqual(data['angles'],['front','three-quarter','side','back','high'])
        checked=set()
        for p in poses:
            path=BASE/p['sprite'];self.assertTrue(path.is_file(),str(path))
            self.assertGreaterEqual(p['spriteRow'],0);self.assertLess(p['spriteRow'],p['spriteRows'])
            if path not in checked:
                with Image.open(path) as im:self.assertEqual(im.size,(p['width']*5,p['height']*p['spriteRows']))
                checked.add(path)
            self.assertTrue((BASE/f'site-assets/thumbs/{p["thumb"]["sheet"]:03d}.webp').is_file())
    def test_no_exact_geometry_duplicates(self):
        data=json.loads((BASE/'poses/gallery-manifest.json').read_text());signatures={}
        fields=['root','pelvis_euler','torso_euler','head_euler','wrists','elbows','ankles','knees','hand_directions','hand_pose','foot_euler','foot_yaw']
        for p in data['poses']:
            signature=json.dumps({k:p.get(k) for k in fields},sort_keys=True)
            self.assertNotIn(signature,signatures,f'Exact duplicate: {p["id"]} and {signatures.get(signature)}')
            signatures[signature]=p['id']
    def test_local_dependencies(self):
        html=(BASE/'index.html').read_text()
        for path in re.findall(r'(?:src|href)="([^"]+)"',html):
            if path.startswith(('http:','https:','#')):continue
            self.assertTrue((BASE/path).is_file(),path)
        self.assertNotIn('cdn.',html)
    def test_generated_index_matches(self):
        text=(BASE/'gallery-data.js').read_text();data=json.loads(text.removeprefix('window.POSE_DATA = ').strip().removesuffix(';'))
        manifest=json.loads((BASE/'poses/gallery-manifest.json').read_text());self.assertEqual(data,manifest)
if __name__=='__main__':unittest.main()
