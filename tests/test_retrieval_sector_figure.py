"""A figura usa os artefactos existentes e escreve na árvore canónica."""

from scripts.figures import fig_retrieval_sector_causal as figure


def test_existing_artifacts_supply_five_sectors_and_two_protocols():
    sectors = figure._sector_rows(
        figure.REPO / "docs/evaluation/evaluation_per_sector.md"
    )
    causal = figure._causal_rows(
        figure.REPO / "docs/evaluation/evaluation_retrieval_causal.md"
    )
    assert {row["Setor"] for row in sectors} == set(figure.SECTOR_LABELS)
    assert [row["protocolo"] for row in causal] == ["simétrico", "causal"]
    assert [float(row["precisão@5"]) for row in causal] == [0.595, 0.513]
    for row in causal:
        assert round(float(row["precisão@5"]) - float(row["chão"]), 3) == float(row["margem"])


def test_default_output_is_canonical(monkeypatch):
    captured = []
    monkeypatch.setattr("sys.argv", ["figure"])
    monkeypatch.setattr(figure, "build", lambda *args: captured.append(args))
    figure.main()
    assert captured[0][2] == figure.REPO / "tese-v2/figures/eval_retrieval_sector_causal.pdf"
