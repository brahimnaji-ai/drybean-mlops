import subprocess
NAVY="#1F3A5F"; TEAL="#2A9D8F"; GREY="#8A94A0"
dot = f'''
digraph UC {{
  rankdir=LR; splines=true; nodesep=0.35; ranksep=0.9; bgcolor="white";
  fontname="DejaVu Sans"; node [fontname="DejaVu Sans", fontsize=11]; edge [fontname="DejaVu Sans", fontsize=9, color="{NAVY}"];
  node [shape=none, label=""];
  eng  [image="img/actor.png", label="ML Engineer", labelloc=b, imagepos="tc"];
  api  [image="img/actor.png", label="API Consumer\\n(inspection system)", labelloc=b, imagepos="tc"];
  ci   [image="img/actor.png", label="GitHub Actions\\n(CI/CD + scheduler)", labelloc=b, imagepos="tc"];
  subgraph cluster_sys {{
    label="Dry Bean MLOps platform"; style="rounded"; color="{NAVY}"; fontcolor="{NAVY}"; fontsize=13; labeljust=l;
    node [shape=ellipse, style=filled, fillcolor="#EAF2F8", color="{NAVY}", margin="0.12,0.06"];
    uc1 [label="Classify bean"]; uc2 [label="Check service health"]; uc3 [label="Submit true label"];
    uc4 [label="Ingest data batch"]; uc5 [label="Validate data"]; uc6 [label="Train candidate model"];
    uc7 [label="Evaluate and compare\\nwith champion"]; uc8 [label="Promote model"]; uc9 [label="Deploy service"];
    uc10 [label="Generate drift report"]; uc11 [label="Roll back release"]; uc12 [label="Browse experiments"];
    uc13 [label="Open alert on drift"];
  }}
  api -> uc1 [arrowhead=none]; api -> uc2 [arrowhead=none]; api -> uc3 [arrowhead=none];
  eng -> uc4 [arrowhead=none]; eng -> uc12 [arrowhead=none]; eng -> uc10 [arrowhead=none];
  uc5 -> ci [arrowhead=none]; uc6 -> ci [arrowhead=none]; uc9 -> ci [arrowhead=none]; uc10 -> ci [arrowhead=none]; uc11 -> ci [arrowhead=none];
  edge [style=dashed, color="{TEAL}", fontcolor="{TEAL}", arrowhead=open];
  uc4 -> uc5 [label="«include»"]; uc6 -> uc5 [label="«include»"];
  uc8 -> uc7 [label="«extend»\\n[strictly better F1]"];
  uc8 -> uc9 [label="«include»"];
  uc11 -> uc9 [label="«extend»\\n[smoke test fails]"];
  uc13 -> uc10 [label="«extend»\\n[drift detected]"];
}}
'''
open("uc.dot","w").write(dot)
subprocess.run(["dot","-Tpng","-Gdpi=170","uc.dot","-o","img/usecase.png"],check=True)
