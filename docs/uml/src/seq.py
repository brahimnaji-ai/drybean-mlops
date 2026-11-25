import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
NAVY="#1F3A5F"; TEAL="#2A9D8F"; GREY="#8A94A0"; AMB="#E9A23B"; RED="#C0392B"
plt.rcParams["font.family"]="DejaVu Sans"

def draw(parts, msgs, frames, fname, title, w=15, rowh=0.62):
    n=len(msgs); H=n*rowh+3.4
    fig,ax=plt.subplots(figsize=(w,H*0.62),dpi=170)
    xs={p:i*(w-3.0)/(len(parts)-1)+1.5 for i,p in enumerate(parts)}
    top=H-1.1
    for p,x in xs.items():
        ax.add_patch(FancyBboxPatch((x-0.78,top-0.5),1.56,0.7,boxstyle="round,pad=0.02",fc="#EAF2F8",ec=NAVY,lw=1.4))
        ax.text(x,top-0.15,p,ha="center",va="center",fontsize=8.5,fontweight="bold",color=NAVY)
        ax.plot([x,x],[top-0.5,0.3],color=GREY,lw=1,ls=(0,(4,3)))
    ys=[top-1.1-i*rowh for i in range(n)]
    # frames first (behind)
    for (kind,a,b,label,els) in frames:
        x0=min(xs.values())-1.1; x1=max(xs.values())+1.1
        y0=ys[a]+rowh*0.75; y1=ys[b]-rowh*0.45
        ax.add_patch(Rectangle((x0,y1),x1-x0,y0-y1,fill=False,ec=AMB,lw=1.3))
        ax.add_patch(Rectangle((x0,y0-0.3),1.1,0.3,fc=AMB,ec=AMB))
        ax.text(x0+0.55,y0-0.15,kind,ha="center",va="center",fontsize=7.5,fontweight="bold",color="white")
        ax.text(x0+1.2,y0-0.15,label,ha="left",va="center",fontsize=7.5,color="#7A5410",style="italic")
        if els is not None:
            ye=ys[els]+rowh*0.75
            ax.plot([x0,x1],[ye,ye],color=AMB,lw=1.1,ls=(0,(5,3)))
            ax.text(x0+0.15,ye-0.15,"[else]",fontsize=7.5,color="#7A5410",style="italic",va="center")
    for i,(a,b,label,kind) in enumerate(msgs):
        y=ys[i]; xa,xb=xs[a],xs[b]
        col = RED if kind=="err" else (TEAL if kind=="ret" else NAVY)
        ls = (0,(4,3)) if kind in("ret","err") else "-"
        if a==b:
            ax.plot([xa,xa+0.55,xa+0.55,xa+0.05],[y+0.12,y+0.12,y-0.12,y-0.12],color=col,lw=1.2)
            ax.annotate("",xy=(xa+0.02,y-0.12),xytext=(xa+0.2,y-0.12),arrowprops=dict(arrowstyle="-|>",color=col,lw=1.2))
            ax.text(xa+0.65,y,f"{i+1}. {label}",fontsize=7.8,va="center",ha="left",color=col,bbox=dict(fc="white",ec="none",pad=1.2))
        else:
            ax.annotate("",xy=(xb,y),xytext=(xa,y),arrowprops=dict(arrowstyle="-|>" if kind!="ret" else "->",color=col,lw=1.3,ls=ls,shrinkA=0,shrinkB=0))
            ax.text((xa+xb)/2,y+0.07,f"{i+1}. {label}",fontsize=7.8,va="bottom",ha="center",color=col,bbox=dict(fc="white",ec="none",pad=1.0))
    ax.text(0.3,H-0.1,title,fontsize=11,fontweight="bold",color=NAVY,va="top")
    ax.set_xlim(0,w); ax.set_ylim(0,H); ax.axis("off")
    fig.savefig(fname,bbox_inches="tight",pad_inches=0.1,facecolor="white"); plt.close(fig)

P1=["Developer","GitHub Actions","DVC remote","TrainingPipeline","ModelRegistry","PromotionPolicy","GHCR","Host (API)"]
M1=[
("Developer","GitHub Actions","push to main  /  new data (.dvc pointer changed)","sync"),
("GitHub Actions","DVC remote","dvc pull   (retry x3, exponential backoff)","sync"),
("DVC remote","GitHub Actions","dataset vX + golden test set","ret"),
("GitHub Actions","TrainingPipeline","run(params.yaml)","sync"),
("TrainingPipeline","TrainingPipeline","validate, preprocess, fit, evaluate, log run to MLflow","sync"),
("TrainingPipeline","ModelRegistry","get_champion().metrics","sync"),
("ModelRegistry","TrainingPipeline","champion metrics (or none on first run)","ret"),
("TrainingPipeline","PromotionPolicy","decide(candidate, champion)","sync"),
("PromotionPolicy","TrainingPipeline","PROMOTE","ret"),
("GitHub Actions","GHCR","build + push image :sha with candidate model","sync"),
("GitHub Actions","Host (API)","deploy image, then smoke test GET /health","sync"),
("Host (API)","GitHub Actions","200 healthy   (else rollback to previous tag, stop)","ret"),
("TrainingPipeline","ModelRegistry","commit champion pointer (champion.json + dvc push model)","sync"),
("PromotionPolicy","TrainingPipeline","RETAIN champion","ret"),
("GitHub Actions","Developer","report only: metrics + reason, no deploy","ret"),
]
F1=[("alt",8,12,"candidate F1 strictly greater than champion F1",13)]
draw(P1,M1,F1,"img/seq_promote.png","Sequence - retrain and conditional deploy (two-phase promotion)",w=16)

P2=["API Client","RestController","PredictionService","Classifier","PredictionLogger"]
M2=[
("API Client","RestController","POST /predict {16 measurements}","sync"),
("RestController","RestController","validate body (Pydantic)","sync"),
("RestController","API Client","400 / 422 error body","err"),
("RestController","PredictionService","classify(request)","sync"),
("PredictionService","Classifier","predict_proba(features)","sync"),
("Classifier","PredictionService","probabilities","ret"),
("PredictionService","PredictionLogger","log(request_id, features, prediction, model_version)","sync"),
("PredictionService","RestController","bean_class, probabilities, version","ret"),
("RestController","API Client","200 {bean_class, probabilities, model_version}","ret"),
("PredictionService","RestController","ModelUnavailable","err"),
("RestController","API Client","503 {detail}","err"),
]
F2=[("alt",2,2,"body invalid",None),("alt",4,8,"model loaded",9),]
draw(P2,M2,[("alt",2,2,"body invalid",None),("alt",4,8,"model loaded",9)],"img/seq_predict.png","Sequence - POST /predict",w=13,rowh=0.8)
