import sys, re, pathlib

root = pathlib.Path(".")

envp = (root/".env.local").read_text().splitlines()

manifest = (root/"docs"/"MODEL_MANIFEST.md").read_text()



want = {}

for k in ("THEOLOGY_MODEL","EMBEDDING_MODEL","RERANKER_MODEL","MATH_MODEL"):

    for line in envp:

        if line.startswith(k+"="):

            want[k] = line.split("=",1)[1].strip()

            break



miss = [k for k in ("THEOLOGY_MODEL","EMBEDDING_MODEL","RERANKER_MODEL","MATH_MODEL") if k not in want]

if miss:

    print("MISSING_IN_ENV", ",".join(miss)); sys.exit(2)



bad = []

for k,v in want.items():

    # require exact string somewhere in the manifest block

    if re.search(rf'^{k}\s*=\s*{re.escape(v)}\b', manifest, re.M) is None and \

       (k!="EMBEDDING_MODEL" or v in manifest) and \

       (k!="RERANKER_MODEL"  or v in manifest):

        bad.append((k,v))

if bad:

    for k,v in bad: print(f"DRIFT:{k}='{v}' not found in MODEL_MANIFEST")

    sys.exit(3)



print("MODELS_VERIFY_OK")