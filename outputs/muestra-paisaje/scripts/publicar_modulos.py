"""Convert exported .mlmod files to versioned static catalog folders.

python scripts/publicar_modulos.py paquete.mlmod [otro.mlmod ...]
python scripts/publicar_modulos.py --remove mod:ID
python scripts/publicar_modulos.py --restore mod:ID
No network, Git operations or permanent deletion are performed.
"""
import argparse,base64,hashlib,json,re,struct
from pathlib import Path

MAX=80*1024*1024
CATEGORIES={'decor','buildings','animals','people','vehicles','ranch','plants'}

def validate(raw):
    if raw.get('format')!='medialuna-module' or raw.get('version')!=1: raise ValueError('Paquete .mlmod inválido')
    asset=base64.b64decode(raw['glb'],validate=True)
    if not 20<=len(asset)<=MAX: raise ValueError('GLB fuera del límite de 80 MB')
    magic,version,total,chunk_len,chunk_type=struct.unpack_from('<5I',asset)
    if (magic,version,total,chunk_type)!=(0x46546c67,2,len(asset),0x4e4f534a) or chunk_len+20>len(asset): raise ValueError('GLB inválido')
    document=json.loads(asset[20:20+chunk_len])
    for resource in document.get('buffers',[])+document.get('images',[]):
        uri=resource.get('uri','')
        if uri and not uri.startswith(('data:image/','data:application/octet-stream')): raise ValueError('GLB con recursos externos')
    if document.get('skins'): raise ValueError('Solo módulos estáticos sin rig')
    if set(document.get('extensionsRequired',[])) & {'KHR_draco_mesh_compression','EXT_meshopt_compression','KHR_texture_basisu'}: raise ValueError('Compresión no compatible')
    identifier='mod:'+hashlib.sha256(asset).hexdigest()[:24]
    if raw.get('id')!=identifier: raise ValueError('ID no coincide con el archivo')
    if raw.get('category') not in CATEGORIES or not isinstance(raw.get('name'),str) or not 1<=len(raw['name'].strip())<=80: raise ValueError('Ficha inválida')
    height=raw.get('height');yaw=raw.get('yaw',0)
    import math
    if not isinstance(height,(int,float)) or not .05<=height<=100 or not isinstance(yaw,(int,float)) or not math.isfinite(yaw): raise ValueError('Medidas inválidas')
    return dict(id=identifier,name=raw['name'].strip(),category=raw['category'],height=height,yaw=yaw),asset

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packages',nargs='*',type=Path)
    group=parser.add_mutually_exclusive_group();group.add_argument('--remove');group.add_argument('--restore')
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1],help='Carpeta del sitio que contiene catalogo/')
    args=parser.parse_args();root=args.root.resolve();catalog=root/'catalogo';catalog.mkdir(parents=True,exist_ok=True)
    # Validate every supplied package before writing any of them.
    prepared=[]
    for path in args.packages:
        if path.stat().st_size>115*1024*1024: raise ValueError('Paquete demasiado grande')
        prepared.append(validate(json.loads(path.read_text(encoding='utf8'))))
    for meta,asset in prepared:
        folder=catalog/'modulos'/meta['id'][4:];folder.mkdir(parents=True,exist_ok=True)
        existing=folder/'modelo.glb'
        if existing.exists() and existing.read_bytes()!=asset: raise ValueError('ID ya existente con otro modelo')
        existing.write_bytes(asset)
        (folder/'ficha.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    identifier=args.remove or args.restore
    if identifier:
        if not re.fullmatch(r'mod:[a-z0-9_-]{1,80}',identifier): raise ValueError('ID inválido')
        ficha=catalog/'modulos'/identifier[4:]/'ficha.json'
        meta=json.loads(ficha.read_text(encoding='utf8'));meta['retired']=bool(args.remove)
        ficha.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    modules=[]
    for file in sorted((catalog/'modulos').glob('*/ficha.json')):
        meta=json.loads(file.read_text(encoding='utf8'))
        # Retired files stay in Git to keep existing maps recoverable.
        meta['file']='modulos/'+file.parent.name+'/modelo.glb';modules.append(meta)
    manifest=catalog/'manifest.json';temp=catalog/'manifest.tmp'
    temp.write_text(json.dumps({'version':1,'modules':modules},ensure_ascii=False,indent=2)+'\n',encoding='utf8');temp.replace(manifest)
    print(f'Catálogo preparado: {len(modules)} módulos. Revisa y sube catalogo/ a GitHub.')
if __name__=='__main__': main()
