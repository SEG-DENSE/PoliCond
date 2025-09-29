import os

import matplotlib.pyplot as plt
import pandas as pd
import prettytable

TARGET_DIR = r"datasets\apps-PoliCond-DeepSeek\contradiction"
sample_path = os.path.join(TARGET_DIR, "sample.csv")
contradiction_context_path = os.path.join(TARGET_DIR, r"contradiction_context.csv")
contradiction_pair_path = os.path.join(TARGET_DIR, r"contradiction_pair.csv")


def show_sample_percentage():
    df = pd.read_csv(sample_path, encoding_errors="ignore", encoding="utf-8-sig")

    label_counts = df["label"].value_counts()
    total = label_counts.sum()

    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False

    def make_autopct(values):
        def my_autopct(pct):
            val = int(round(pct * total / 100.0))
            return f"{pct:.1f}%\n({val})"

        return my_autopct

    plt.figure(figsize=(10, 8))
    patches, texts, autotexts = plt.pie(
        label_counts,
        autopct=make_autopct(label_counts),
        startangle=140,
        colors=plt.cm.tab20(range(len(label_counts))),
        wedgeprops=dict(width=0.3, edgecolor="w"),
        textprops={"fontsize": 12},
    )

    plt.title(
        "Label Distribution For Verified Contradiction Contexts", fontsize=14, pad=20
    )
    plt.axis("equal")

    # for text in texts:
    #     text.set_color('black')
    #     text.set_fontsize(14)
    for autotext in autotexts:
        autotext.set_color("black")
        autotext.set_fontsize(14)

    centre_circle = plt.Circle((0, 0), 0.70, fc="white")
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    plt.legend(
        patches,
        label_counts.index,
        title="Category",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        frameon=False,
    )

    plt.tight_layout()
    plt.show()


def show_sample_table():
    header = [
        "granularity",
        "verifiedCount",
        "contrCnt",
        "contrRatio",
        "nonContrCnt",
        "noncontrRatio",
    ]
    table = prettytable.PrettyTable(header)
    df = pd.read_csv(sample_path, encoding_errors="ignore", encoding="utf-8-sig")

    verified_cxt_cnt = df.count().values[0]
    contrContextCnt = df[df["label"] > 0].count().values[0]

    row1 = {
        "granularity": "context",
        "verifiedCount": verified_cxt_cnt,
        "contrCnt": contrContextCnt,
        "contrRatio": str(round(contrContextCnt / verified_cxt_cnt * 100, 2)) + "%",
        "nonContrCnt": verified_cxt_cnt - contrContextCnt,
        "nonContrRatio": str(
            round((verified_cxt_cnt - contrContextCnt) / verified_cxt_cnt * 100, 2)
        )
        + "%",
    }
    fileCount = len(df["filename"].unique())
    contrCnt = len(df[df["label"] > 0]["filename"].unique())
    row2 = {
        "granularity": "file",
        "verifiedCount": fileCount,
        "contrCnt": contrCnt,
        "contrRatio": str(round(contrCnt / fileCount * 100, 2)) + "%",
        "nonContrCnt": fileCount - contrCnt,
        "nonContrRatio": str(round((fileCount - contrCnt) / fileCount * 100, 2)) + "%",
    }
    df2 = pd.read_csv(
        contradiction_pair_path, encoding_errors="ignore", encoding="utf-8-sig"
    )
    df2 = df2[df2["label"] != -1]
    verifiedPairCount = df2["label"].count()
    contrCnt = df2[df2["label"] > 0]["label"].count()
    row3 = {
        "granularity": "pair",
        "verifiedPairCount": verifiedPairCount,
        "contrCnt": contrCnt,
        "contrRatio": str(round(contrCnt / verifiedPairCount * 100, 2)) + "%",
        "nonContrCnt": verifiedPairCount - contrCnt,
        "nonContrRatio": str(
            round((verifiedPairCount - contrCnt) / verifiedPairCount * 100, 2)
        )
        + "%",
    }

    table.add_row(row1.values())
    table.add_row(row2.values())
    table.add_row(row3.values())

    table.align = "l"
    table.float_format = ".2"
    table.padding_width = 1
    table.max_width = 20

    print(table)


if __name__ == "__main__":
    show_sample_percentage()
    show_sample_table()
