import pandas as pd

chemin = "fr-en-dnma-par-uai-appareils.csv"

df = pd.read_csv(chemin, sep=";", dtype={"UAI": "string"})

df["debutSemaine"] = pd.to_datetime(df["debutSemaine"], errors="coerce")
df_2025 = df[(df["UAI"] == "0010024W") & (df["debutSemaine"].dt.year == 2025)].copy()

visit_cols = [
    "visites_ordinateur",
    "visites_smartphone",
    "visites_tablette",
    "visites_autreappareil",
]

for c in visit_cols:
    df_2025[c] = pd.to_numeric(df_2025[c], errors="coerce").fillna(0)

df_2025["Nb Visites"] = df_2025[visit_cols].sum(axis=1)

top3 = (
    df_2025[["debutSemaine", "Nb Visites"]]
    .sort_values("Nb Visites", ascending=False)
    .head(3)
)

print(top3.to_string(index=False))