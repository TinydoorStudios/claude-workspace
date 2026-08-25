import numpy as np, trimesh, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
m=trimesh.load("nametag_jig.stl")
b=m.bounds; W,H,T=b[1]-b[0]
fig=plt.figure(figsize=(15,6))

ax=fig.add_subplot(121,projection='3d')
sh=0.35+0.65*np.clip(m.face_normals@np.array([0.3,-0.5,0.81]),0,1)
c=np.zeros((len(m.faces),4)); c[:,0]=0.18+0.5*sh; c[:,1]=0.43+0.42*sh; c[:,2]=0.64+0.3*sh; c[:,3]=1
ax.add_collection3d(Poly3DCollection(m.triangles,facecolors=c,linewidths=0))
ax.set_xlim(b[0][0],b[1][0]); ax.set_ylim(b[0][1],b[1][1]); ax.set_zlim(0,40)
ax.set_box_aspect((W,H,25)); ax.view_init(elev=55,azim=-60); ax.axis('off')
ax.set_title(f"nametag_jig.stl  —  {W:.2f} × {H:.2f} × {T:.2f} mm",fontsize=13,weight='bold')

bx=fig.add_subplot(122)
up=m.face_normals[:,2]>0.99
flat=np.abs(m.triangles[:,:,2].max(axis=1)-m.triangles[:,:,2].min(axis=1))<1e-6
for i in np.where(up&flat)[0]:
    t=m.triangles[i]
    col='#d9d9d4' if abs(t[0,2]-T)<1e-6 else '#3aa76d'
    bx.fill(t[:,0],t[:,1],facecolor=col,edgecolor='none')
bx.set_aspect('equal'); bx.set_xlim(-4,W+4); bx.set_ylim(-4,H+4)
bx.set_title("plan — grey = top face, green = pocket floor (depth 1.00 mm)",fontsize=12,weight='bold')
bx.annotate("",xy=(0,-2),xytext=(W,-2),arrowprops=dict(arrowstyle='<|-|>',lw=1.8,color='#333'))
bx.text(W/2,-3.4,f"{W:.2f}",ha='center',va='top',fontsize=10,weight='bold')
bx.annotate("",xy=(-2,0),xytext=(-2,H),arrowprops=dict(arrowstyle='<|-|>',lw=1.8,color='#333'))
bx.text(-3.4,H/2,f"{H:.2f}",rotation=90,ha='right',va='center',fontsize=10,weight='bold')
bx.axis('off')
plt.tight_layout(); plt.savefig("nametag_jig_preview.png",dpi=115,facecolor='white')
print("saved nametag_jig_preview.png")
