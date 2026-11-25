import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
def actor(path, color="#1F3A5F", dashed=False):
    fig, ax = plt.subplots(figsize=(0.9,1.3), dpi=200)
    ls = (0,(3,2)) if dashed else "-"
    ax.add_patch(plt.Circle((0.5,0.82),0.12,fill=False,ec=color,lw=2,ls=ls))
    for (x1,y1,x2,y2) in [(0.5,0.70,0.5,0.38),(0.25,0.58,0.75,0.58),(0.5,0.38,0.28,0.08),(0.5,0.38,0.72,0.08)]:
        ax.plot([x1,x2],[y1,y2],color=color,lw=2,ls=ls,solid_capstyle="round")
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    fig.savefig(path, transparent=True, bbox_inches="tight", pad_inches=0.02); plt.close(fig)
actor("img/actor.png"); actor("img/actor_dash.png", "#8A94A0", True)

actor("img/actor_grey.png","#8A94A0")
