import subprocess
NAVY="#1F3A5F"; TEAL="#2A9D8F"; GREY="#8A94A0"
NODES={}
def cls(id, name, attrs=(), methods=(), stereo=None, fill="#EAF2F8"):
    head = (f'<I>&laquo;{stereo}&raquo;</I><BR/>' if stereo else '') + f'<B>{name}</B>'
    rows = [f'<TR><TD BGCOLOR="{fill}" ALIGN="CENTER">{head}</TD></TR>',
            '<TR><TD ALIGN="LEFT" BALIGN="LEFT">' + ('<BR/>'.join(attrs) if attrs else ' ') + '</TD></TR>',
            '<TR><TD ALIGN="LEFT" BALIGN="LEFT">' + ('<BR/>'.join(methods) if methods else ' ') + '</TD></TR>']
    NODES[id]=f'{id} [shape=plain, label=<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="3" COLOR="{NAVY}">' + ''.join(rows) + '</TABLE>>];\n'
I="#FFF4DD"
cls("RestController","RestController",[],["+predict(m: BeanMeasurements): PredictionResponse","+health(): HealthStatus","+feedback(fb): None"])
cls("BeanMeasurements","BeanMeasurements",["+area, perimeter: float","+major_axis_length, minor_axis_length","+aspect_ratio, eccentricity ...","+shape_factor_1 .. shape_factor_4","(16 validated numeric fields)"],[],"Pydantic")
cls("PredictionResponse","PredictionResponse",["+bean_class: str","+probabilities: dict[str, float]","+model_version: str"],[],"Pydantic")
cls("PredictionService","PredictionService",["-registry: ModelRegistry","-logger: PredictionLogger"],["+classify(m): PredictionResponse"],"Facade")
cls("Classifier","Classifier",[],["+fit(X, y)","+predict_proba(X): ndarray"],"interface",fill=I)
cls("LogRegModel","LogRegModel",["-C: float","-pipeline: FeaturePipeline"],[])
cls("RandomForestModel","RandomForestModel",["-n_estimators: int","-pipeline: FeaturePipeline"],[])
cls("ClassifierFactory","ClassifierFactory",[],["+create(cfg): Classifier"],"Factory")
cls("FeaturePipeline","FeaturePipeline",["-scaler: StandardScaler","-columns: list[str]"],["+fit(X)","+transform(X)"])
cls("TrainingPipeline","TrainingPipeline",["-factory, -validator, -evaluator","-policy, -registry, -data"],["+run(): ModelVersion","#load_data()","#validate()","#fit()","#evaluate()","#register()"],"Template Method")
cls("DataValidator","DataValidator",[],["+validate(df): ValidationReport"])
cls("Dataset","Dataset",["+path: str","+version: str  (DVC md5)","+kind: base|batch|golden"],[])
cls("Evaluator","Evaluator",[],["+evaluate(model, ds): EvaluationResult"])
cls("EvaluationResult","EvaluationResult",["+macro_f1: float","+accuracy: float","+per_class_f1: dict","+confusion_matrix: ndarray"],[])
cls("PromotionPolicy","PromotionPolicy",[],["+decide(cand, champ): Decision"],"interface",fill=I)
cls("StrictImprovementPolicy","StrictImprovementPolicy",["-metric = macro_f1"],["+decide(cand, champ): Decision"])
cls("ModelVersion","ModelVersion",["+version: str","+run_id: str","+data_version: str","+git_sha: str","+stage: Stage"],[])
cls("ModelRegistry","ModelRegistry",[],["+register(mv)","+get_champion(): ModelVersion","+promote(mv)","+archive(mv)"],"interface",fill=I)
cls("MlflowModelRegistry","MlflowModelRegistry",[],[])
cls("GitDvcChampionRegistry","GitDvcChampionRegistry",["-champion.json","-model on DVC"],[])
cls("DataRepository","DataRepository",[],["+pull(version): Dataset","+push(ds)"],"interface",fill=I)
cls("DvcDataRepository","DvcDataRepository",[],[])
cls("PredictionLogger","PredictionLogger",[],["+log(m, resp)","+window(days): DataFrame"])
cls("DriftMonitor","DriftMonitor",[],["+report(ref, cur): DriftReport"],"interface",fill=I)
cls("EvidentlyDriftMonitor","EvidentlyDriftMonitor",[],[])
cls("DriftReport","DriftReport",["+drift_share: float","+drifted_columns: list","+html_path: str"],[])
e=""
def real(a,b): return f'{a} -> {b} [arrowhead=onormal, style=dashed, color="{NAVY}"];\n'
def use(a,b): return f'{a} -> {b} [arrowhead=vee, color="{NAVY}"];\n'
def dep(a,b,l=""): return f'{a} -> {b} [arrowhead=vee, style=dashed, color="{TEAL}", fontcolor="{TEAL}", label="{l}"];\n'
def comp(a,b): return f'{a} -> {b} [arrowhead=none, arrowtail=diamond, dir=both, color="{NAVY}"];\n'
e+=use("RestController","PredictionService")+dep("RestController","BeanMeasurements","uses")+dep("RestController","PredictionResponse","returns")
e+=use("PredictionService","ModelRegistry")+use("PredictionService","PredictionLogger")+use("PredictionService","Classifier")
e+=real("LogRegModel","Classifier")+real("RandomForestModel","Classifier")+comp("LogRegModel","FeaturePipeline")+comp("RandomForestModel","FeaturePipeline")
e+=dep("ClassifierFactory","Classifier","creates")
e+=use("TrainingPipeline","ClassifierFactory")+use("TrainingPipeline","DataValidator")+use("TrainingPipeline","Evaluator")+use("TrainingPipeline","PromotionPolicy")+use("TrainingPipeline","ModelRegistry")+use("TrainingPipeline","DataRepository")
e+=dep("TrainingPipeline","ModelVersion","creates")+dep("Evaluator","EvaluationResult","returns")+comp("ModelVersion","EvaluationResult")
e+=real("StrictImprovementPolicy","PromotionPolicy")+dep("PromotionPolicy","ModelVersion","compares")
e+=real("MlflowModelRegistry","ModelRegistry")+real("GitDvcChampionRegistry","ModelRegistry")+f'ModelRegistry -> ModelVersion [arrowhead=odiamond, dir=back, color="{NAVY}"];\n'
e+=real("DvcDataRepository","DataRepository")+dep("DataRepository","Dataset")
e+=real("EvidentlyDriftMonitor","DriftMonitor")+dep("DriftMonitor","DriftReport")+use("DriftMonitor","PredictionLogger")+dep("DriftMonitor","Dataset","reference")
views={"class_serving":["RestController","BeanMeasurements","PredictionResponse","PredictionService","Classifier","LogRegModel","RandomForestModel","FeaturePipeline","PredictionLogger","ModelRegistry"],
"class_training":["TrainingPipeline","ClassifierFactory","Classifier","DataValidator","Dataset","DataRepository","DvcDataRepository","Evaluator","EvaluationResult","PromotionPolicy","StrictImprovementPolicy","ModelVersion","ModelRegistry","MlflowModelRegistry","GitDvcChampionRegistry"],
"class_monitoring":["DriftMonitor","EvidentlyDriftMonitor","DriftReport","PredictionLogger","Dataset"]}
for name,ids in views.items():
    nn="".join(NODES[i] for i in ids)
    ee="".join(l+"\n" for l in e.split("\n") if l.strip() and l.split(" -> ")[0] in ids and l.split(" -> ")[1].split(" ")[0] in ids)
    dot=f'''digraph C {{ rankdir=TB; nodesep=0.4; ranksep=0.65; splines=true; bgcolor="white";
node [fontname="DejaVu Sans", fontsize=10]; edge [fontname="DejaVu Sans", fontsize=9];
{nn}{ee}}}'''
    open(name+".dot","w").write(dot)
    subprocess.run(["dot","-Tpng","-Gdpi=170",name+".dot","-o","img/"+name+".png"],check=True)
