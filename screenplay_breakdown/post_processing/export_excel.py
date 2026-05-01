import pandas as pd
import os

def export_all(scenes):
    output_path = "post_processing/output/ajeya_shot_breakdown.xlsx"

    df = build_shot_df(scenes)
    df_char = build_character_catalog(df)
    df_asset = build_asset_catalog(df)
    df_loc = build_location_catalog(df)

    write_excel(df, df_char, df_asset, df_loc, output_path)
    return output_path

def build_shot_df(scenes):
    all_rows = []
    for scene in scenes:
        all_rows.extend(scene.shot_rows)

    df = pd.DataFrame(all_rows)

    cols_to_fill = [
        "Weapons", "Animals", "Vehicles / Mounts",
        "Featured Extras / Groups",
        "VFX / SFX / Stunts",
        "Continuity / Production Notes"
    ]

    for col in cols_to_fill:
        if col in df.columns:
            df[col] = df[col].replace(r"^\s*$", "N/A", regex=True).fillna("N/A")

    return df


def build_character_catalog(df):
    char_data = {}

    for _, row in df.iterrows():
        chars = str(row["Characters in Shot"]).split(",")

        for c in chars:
            c = c.strip()
            if c and c != "N/A":
                if c not in char_data:
                    char_data[c] = {
                        "Character": c,
                        "First Seen": row["Scene No."],
                        "Scene Count": set()
                    }
                char_data[c]["Scene Count"].add(row["Scene No."])

    rows = []
    for v in char_data.values():
        rows.append({
            "Character/Group": v["Character"],
            "Type": "",
            "First Seen": v["First Seen"],
            "Notes": "",
            "Scene/Shot Count": len(v["Scene Count"])
        })

    return pd.DataFrame(rows)


def build_asset_catalog(df):
    asset_data = {}

    def add_asset(asset, category, scene):
        if asset and asset != "N/A":
            if asset not in asset_data:
                asset_data[asset] = {
                    "Asset": asset,
                    "Category": category,
                    "Scene(s)": set(),
                    "Usage/Continuity": "",
                    "Notes": ""
                }
            asset_data[asset]["Scene(s)"].add(scene)

    for _, row in df.iterrows():
        scene = row["Scene No."]

        for p in str(row["Props / Set Dressing"]).split(","):
            add_asset(p.strip(), "Prop", scene)

        for w in str(row["Weapons"]).split(","):
            add_asset(w.strip(), "Weapon", scene)

    rows = []
    for v in asset_data.values():
        rows.append({
            "Asset": v["Asset"],
            "Category": v["Category"],
            "Scene(s)": ", ".join(sorted(v["Scene(s)"])),
            "Usage/Continuity": v["Usage/Continuity"],
            "Notes": v["Notes"]
        })

    return pd.DataFrame(rows)


def build_location_catalog(df):
    loc_data = {}

    for _, row in df.iterrows():
        loc = row["Location / Environment"]
        scene = row["Scene No."]

        if loc and loc != "N/A":
            if loc not in loc_data:
                loc_data[loc] = set()
            loc_data[loc].add(scene)

    rows = []
    for loc, scene_set in loc_data.items():
        rows.append({
            "Location/Environment": loc,
            "Key Requirements": "",
            "Scene(s)": ", ".join(sorted(scene_set)),
            "Storyboard Continuity Notes": ""
        })

    return pd.DataFrame(rows)


def write_excel(df, df_char, df_asset, df_loc,output_path):
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Shot Breakdown", index=False)
        df_char.to_excel(writer, sheet_name="Character Catalog", index=False)
        df_asset.to_excel(writer, sheet_name="Asset Catalog", index=False)
        df_loc.to_excel(writer, sheet_name="Location Catalog", index=False)

        for sheet_name in writer.sheets:
            ws = writer.sheets[sheet_name]
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions

            for col in ws.columns:
                max_len = 0
                col_letter = col[0].column_letter

                for cell in col:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))

                ws.column_dimensions[col_letter].width = min(max_len + 2, 40)