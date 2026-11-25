import subprocess
NAVY="#1F3A5F"; TEAL="#2A9D8F"; GREY="#8A94A0"; AMB="#E9A23B"; RED="#C0392B"
BASE='fontname="DejaVu Sans"'
def render(name, dot, dpi=170):
    open(f"{name}.dot","w").write(dot)
    subprocess.run(["dot","-Tpng",f"-Gdpi={dpi}",f"{name}.dot","-o",f"img/{name}.png"],check=True)

# ---------- communication ----------
def obj(i,l): return f'{i} [shape=box, style="filled", fillcolor="#EAF2F8", color="{NAVY}", label=<<U>{l}</U>>];\n'
comm = f'''digraph COM {{ rankdir=LR; nodesep=0.9; ranksep=1.6; bgcolor="white";
node [{BASE}, fontsize=11]; edge [{BASE}, fontsize=10, color="{NAVY}", fontcolor="{NAVY}", arrowhead=vee];
{obj("sched",":Scheduler (cron)")}{obj("job",":MonitorJob")}{obj("repo",":DataRepository")}{obj("plog",":PredictionLogger")}
{obj("mon",":EvidentlyDriftMonitor")}{obj("store",":ReportStore")}{obj("gh",":GitHub Issues")}
sched -> job [label="1: run_weekly()"];
job -> repo [label="1.1: load_reference()"];
job -> plog [label="1.2: window(days=7)"];
job -> mon [label="1.3: report(ref, cur)"];
job -> store [label="1.4: save(report)"];
job -> gh [label="1.5 [drift_share > threshold]:\\nopen_issue(report)", color="{RED}", fontcolor="{RED}"];
}}'''
render("comm",comm)

# ---------- activity ----------
def act(i,l,fill="#EAF2F8"): return f'{i} [shape=box, style="rounded,filled", fillcolor="{fill}", color="{NAVY}", label="{l}"];\n'
def dec(i,l): return f'{i} [shape=diamond, style=filled, fillcolor="#FFF4DD", color="{AMB}", label="{l}", fontsize=9, margin="0.02,0.02"];\n'
a = f'''digraph ACT {{ rankdir=TB; nodesep=0.45; ranksep=0.3; bgcolor="white";
node [{BASE}, fontsize=10]; edge [{BASE}, fontsize=9, color="{NAVY}", arrowhead=vee];
start [shape=circle, style=filled, fillcolor="{NAVY}", label="", width=0.2];
end1 [shape=doublecircle, style=filled, fillcolor="{NAVY}", label="", width=0.16];
{act("t","Trigger: push to main (code), .dvc pointer\\nchanged (data) or manual dispatch")}
{act("lint","Lint + unit tests (ruff, pytest)")}
{dec("d0","tests pass?")}
{act("pull","dvc pull dataset + golden set (retry x3, backoff)\\nthen validate schema and quality")}
{dec("d1","data ok?")}
{act("tr","Preprocess, train candidate, log MLflow run\\nevaluate on golden set (F1, P, R)")}
{dec("d3","candidate F1 >\\nchampion F1?")}
{act("pro","Commit champion pointer\\n(champion.json + dvc push model)")}
{act("bld","Build + push Docker image (GHCR)")}
{act("dep","Deploy + smoke test GET /health")}
{dec("d4","smoke test ok?")}
{act("rb","Roll back to previous image tag\\nopen incident issue", fill="#FBE5E1")}
{act("ret","Retain champion\\npublish evaluation report")}
{act("fail","Fail job, notify, keep production as is", fill="#FBE5E1")}
start -> t -> lint -> d0;
d0 -> pull [label="yes"]; d0 -> fail [label="no"];
pull -> d1; d1 -> tr [label="yes"]; d1 -> fail [label="no (after retries)"];
tr -> d3;
d3 -> bld [label="yes (strictly)"]; d3 -> ret [label="no / equal"];
bld -> dep -> d4;
d4 -> pro [label="yes"]; d4 -> rb [label="no"];
pro -> end1; rb -> end1; ret -> end1; fail -> end1;
{{rank=same; d0; fail}} {{rank=same; d3; ret}} {{rank=same; d4; rb}}
}}'''
render("activity",a)

# ---------- state ----------
st = f'''digraph ST {{ rankdir=TB; nodesep=0.7; ranksep=0.55; bgcolor="white";
node [{BASE}, fontsize=11, shape=box, style="rounded,filled", fillcolor="#EAF2F8", color="{NAVY}"]; edge [{BASE}, fontsize=9, color="{NAVY}", fontcolor="{NAVY}", arrowhead=vee];
init [shape=circle, style=filled, fillcolor="{NAVY}", label="", width=0.22];
fin [shape=doublecircle, style=filled, fillcolor="{NAVY}", label="", width=0.18];
Trained [label="Trained\\n(MLflow run logged)"]; Evaluated; Candidate [fillcolor="#FFF4DD"]; Rejected [fillcolor="#FBE5E1"]; Releasing [label="Releasing\\n(image built, deploying)", fillcolor="#FFF4DD"];
Champion [fillcolor="#DDF3EE", color="{TEAL}"]; Watch [label="UnderWatch\\n(drift alert)", fillcolor="#FFF4DD"]; Archived [fillcolor="#EEF0F2", color="{GREY}"];
init -> Trained [label="training run ends"];
Trained -> Evaluated [label="evaluate(golden set)"];
Evaluated -> Candidate [label="metrics registered"];
Candidate -> Releasing [label="[F1 strictly greater]\\npromote()"];
Releasing -> Champion [label="[smoke test ok]\\ncommit pointer"];
Releasing -> Rejected [label="[smoke test fails]\\nrollback"];
Candidate -> Rejected [label="[F1 lower or equal]\\nreject()"];
Champion -> Watch [label="drift share above threshold"];
Watch -> Champion [label="no action / false alarm"];
Watch -> Trained [label="retrain triggered", style=dashed];
Champion -> Archived [label="new champion promoted"];
Watch -> Archived [label="new champion promoted"];
Rejected -> Archived [label="retention policy"];
Archived -> fin;
}}'''
render("state",st)

# ---------- architecture ----------
arch = f'''digraph ARCH {{ rankdir=TB; nodesep=0.5; ranksep=0.75; compound=true; bgcolor="white"; newrank=true;
node [{BASE}, fontsize=12, shape=box, style="rounded,filled", fillcolor="#EAF2F8", color="{NAVY}", margin="0.15,0.08"]; edge [{BASE}, fontsize=10, color="{NAVY}", fontcolor="{NAVY}", arrowhead=vee];
client [label="API consumers\\n(banks, telecoms)", shape=ellipse, fillcolor="#FFFFFF"];
subgraph cluster_gh {{ label="GitHub"; style=rounded; color="{NAVY}"; fontcolor="{NAVY}"; fontsize=13; fontname="DejaVu Sans";
  repo [label="Repository\\ncode + .dvc pointers"]; ci [label="Actions workflows\\nci / train-deploy / monitor"]; ghcr [label="GHCR\\nDocker images"]; iss [label="Issues + Project board"]; }}
subgraph cluster_cloud {{ label="Cloud (host to be decided - ADR-002)"; style="rounded,dashed"; color="{AMB}"; fontcolor="#7A5410"; fontsize=13; fontname="DejaVu Sans";
  host [label="Hosted API container\\n(model baked in image)"]; s3 [label="S3-compatible bucket\\nDVC remote + prediction logs"]; }}
subgraph cluster_dev {{ label="Developer machine: docker compose up"; style=rounded; color="{TEAL}"; fontcolor="{TEAL}"; fontsize=13; fontname="DejaVu Sans";
  api [label="FastAPI (local)"]; mlf [label="MLflow server\\n(tracking)"]; minio [label="MinIO\\n(local DVC remote + artifacts)"]; mon [label="Monitor job\\n(Evidently)"]; }}
repo -> ci [label="push / data change"];
ci -> s3 [label="dvc pull (retry)"]; ci -> ghcr [label="push image"]; ci -> host [label="deploy + smoke test"]; ci -> iss [label="alerts, drift issues"];
ghcr -> host [label="pull image"]; client -> host [label="HTTPS"];
host -> s3 [label="write logs", style=dashed]; mon -> s3 [label="read logs", style=dashed];
api -> mlf [label="loads champion (dev)", style=dashed]; mlf -> minio [label="artifacts"]; repo -> minio [label="dvc push/pull (dev)", style=dashed];
mon -> api [label="local logs", style=dashed, constraint=false];
}}'''
render("arch",arch)
