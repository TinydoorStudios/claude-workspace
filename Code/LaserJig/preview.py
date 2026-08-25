import numpy as np, trimesh, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
m=trimesh.load("keyfob_jig_2up.stl")
fig=plt.figure(figsize=(15,6.5))

ax=fig.add_subplot(121,projection='3d')
sh=0.35+0.65*np.clip(m.face_normals@np.array([0.3,-0.5,0.81]),0,1)
c=np.zeros((len(m.faces),4)); c[:,0]=0.18+0.5*sh; c[:,1]=0.43+0.42*sh; c[:,2]=0.64+0.3*sh; c[:,3]=1
ax.add_collection3d(Poly3DCollection(m.triangles,facecolors=c,linewidths=0))
b=m.bounds; ax.set_xlim(b[0][0],b[1][0]); ax.set_ylim(b[0][1],b[1][1]); ax.set_zlim(0,60)
ax.set_box_aspect((94.6,58.8,40)); ax.view_init(elev=52,azim=-58); ax.axis('off')
ax.set_title("keyfob_jig_2up.stl  —  94.62 × 58.78 × 6.00 mm",fontsize=13,weight='bold')

bx=fig.add_subplot(122)
up=m.face_normals[:,2]>0.99
flat=np.abs(m.triangles[:,:,2].max(axis=1)-m.triangles[:,:,2].min(axis=1))<1e-6
for i in np.where(up&flat)[0]:
    t=m.triangles[i]
    col='#d9d9d4' if abs(t[0,2]-6.0)<1e-6 else '#3aa76d'
    bx.fill(t[:,0],t[:,1],facecolor=col,edgecolor='none')
bx.set_aspect('equal'); bx.set_xlim(-4,99); bx.set_ylim(-4,63)
bx.set_title("plan — grey = top face (z 6.00), green = pocket floor (z 2.30)",fontsize=12,weight='bold')
for x,lab in [(25.405,"pocket 1"),(69.215,"pocket 2")]:
    bx.plot(x,29.39,'k+',ms=14,mew=2)
    bx.text(x,29.39-1.5,f"{lab}\nX {x:.2f}  Y 29.39",ha='center',va='top',fontsize=9.5,weight='bold',
            bbox=dict(boxstyle='round,pad=0.3',fc='white',ec='#333',alpha=.9))
bx.annotate("",xy=(0,-2),xytext=(94.62,-2),arrowprops=dict(arrowstyle='<|-|>',lw=1.8,color='#333'))
bx.text(47,-3.4,"94.62",ha='center',va='top',fontsize=10,weight='bold')
bx.annotate("",xy=(-2,0),xytext=(-2,58.78),arrowprops=dict(arrowstyle='<|-|>',lw=1.8,color='#333'))
bx.text(-3.4,29.4,"58.78",rotation=90,ha='right',va='center',fontsize=10,weight='bold')
bx.axis('off')
plt.tight_layout(); plt.savefig("jig_preview.png",dpi=115,facecolor='white')
