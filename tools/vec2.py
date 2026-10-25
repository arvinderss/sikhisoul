# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Sikh Manuscript Revival contributors
"""Robust line-trace: extract ink (dark) or light tooling from crop, vectorize to single-colour SVG.
usage: vec2.py spec.json outdir"""
import sys, json, os, re
import numpy as np, cv2, vtracer
spec=json.load(open(sys.argv[1])); out=sys.argv[2]; os.makedirs(out+'/_png',exist_ok=True)
for s in spec:
    im=cv2.imread(s['src']); h,w=im.shape[:2]
    if s.get('box'):
        x0,y0,x1,y1=s['box']
        if max(s['box'])<=1.0: x0,x1,y0,y1=int(x0*w),int(x1*w),int(y0*h),int(y1*h)
        im=im[y0:y1,x0:x1]
    sc=s.get('scale',3); im=cv2.resize(im,None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC)
    mode=s.get('ink','dark')
    if mode=='red':
        b,g,r=[c.astype(np.float32) for c in cv2.split(im)]
        v=np.clip(r-(g+b)/2,0,255); v=(v/v.max()*255).astype(np.uint8)
        v=cv2.GaussianBlur(v,(3,3),0); _,mask=cv2.threshold(v,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    else:
        g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        if mode=='light': g=255-g
        k=max(31,(min(g.shape)//8)|1)
        bg=cv2.medianBlur(cv2.dilate(g,np.ones((9,9),np.uint8)),k)
        norm=cv2.divide(g,bg,scale=255)
        norm=cv2.GaussianBlur(norm,(3,3),0)
        t=s.get('thresh')
        if t: _,mask=cv2.threshold(norm,t,255,cv2.THRESH_BINARY_INV)
        else: _,mask=cv2.threshold(norm,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    k2=s.get('open',0)
    if k2: mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,np.ones((k2,k2),np.uint8))
    # remove small specks
    n,lab,st,_=cv2.connectedComponentsWithStats(mask,8)
    minA=s.get('minarea',int(40*sc*sc/9))
    keep=np.zeros_like(mask)
    for i in range(1,n):
        if st[i,cv2.CC_STAT_AREA]>=minA: keep[lab==i]=255
    for (bx0,by0,bx1,by1) in s.get('erase',[]):  # erase boxes (fractions of crop)
        H,W=keep.shape; keep[int(by0*H):int(by1*H),int(bx0*W):int(bx1*W)]=0
    png=f"{out}/_png/{s['name']}.png"; cv2.imwrite(png,255-keep)
    svg=f"{out}/{s['name']}.svg"
    vtracer.convert_image_to_svg_py(png,svg,colormode='binary',mode='spline',filter_speckle=4,corner_threshold=60,length_threshold=4.0,splice_threshold=45,path_precision=1)
    t=open(svg).read(); col=s.get('color','#2A2018')
    t=t.replace('fill="#000000"',f'fill="{col}"')
    m=re.search(r'width="(\d+)" height="(\d+)"',t); W,H=m.group(1),m.group(2)
    t=t.replace(f'width="{W}" height="{H}"',f'viewBox="0 0 {W} {H}" width="{W}" height="{H}"',1)
    t=t.replace('<svg ',f'<svg data-source="{s.get("src_label","")}" ',1)
    open(svg,'w').write(t)
    print(s['name'], f"{os.path.getsize(svg)//1024}KB")
