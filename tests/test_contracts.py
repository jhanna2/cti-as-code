"""Contract tests. The seeds pass; each gate has a negative test that constructs the
forbidden shape and asserts rejection. A gate without a negative test is a comment.
"""
import copy
from pathlib import Path

import pytest

from ctiac.loader import Repo, load_repo
from ctiac import schema

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "example"


@pytest.fixture
def repo() -> Repo:
    return load_repo(EXAMPLE)


def test_seeds_validate_clean(repo):
    assert schema.validate(repo) == []


def test_gate_eei_needs_source_or_gap(repo):
    repo.pirs["PIR-03"] = copy.deepcopy(repo.pirs["PIR-03"])
    repo.pirs["PIR-03"]["eei"][0]["sources"] = []
    repo.pirs["PIR-03"]["eei"][0]["gap"] = None
    msgs = [v.message for v in schema.check_requirements(repo)]
    assert any("neither a resolvable source nor a named gap" in m for m in msgs)


def test_gate_active_pir_needs_consumer(repo):
    repo.pirs["PIR-08"] = copy.deepcopy(repo.pirs["PIR-08"])
    repo.pirs["PIR-08"]["consumer"] = []
    assert any("no consumer" in v.message for v in schema.check_requirements(repo))


def test_gate_threat_profile_ref_must_resolve(repo):
    repo.pirs["PIR-03"] = copy.deepcopy(repo.pirs["PIR-03"])
    repo.pirs["PIR-03"]["threat_profile_refs"] = ["CJ-99"]
    assert any("CJ-99" in v.message for v in schema.check_requirements(repo))


def test_gate_candidate_needs_live_pir(repo):
    repo.candidates["DC-07"] = copy.deepcopy(repo.candidates["DC-07"])
    repo.candidates["DC-07"]["pir"] = "PIR-404"
    assert any("does not resolve" in v.message for v in schema.check_candidates(repo))


def test_gate_candidate_must_publish_blind_spot(repo):
    repo.candidates["DC-07"] = copy.deepcopy(repo.candidates["DC-07"])
    repo.candidates["DC-07"]["not_covered"] = []
    assert any("not_covered is empty" in v.message for v in schema.check_candidates(repo))


def test_gate_decoy_needs_plausibility_and_maintenance(repo):
    repo.decoys["DEC-02"] = copy.deepcopy(repo.decoys["DEC-02"])
    repo.decoys["DEC-02"]["plausibility"] = ""
    repo.decoys["DEC-02"]["maintenance"] = {}
    msgs = [v.message for v in schema.check_decoys(repo)]
    assert any("plausibility" in m for m in msgs)
    assert any("refresh_days" in m for m in msgs)


def test_gate_source_must_say_where_it_lives(repo):
    # A source you cannot locate is a source you cannot audit or replace.
    repo.sources["SRC-04"] = copy.deepcopy(repo.sources["SRC-04"])
    repo.sources["SRC-04"]["provenance"]["store"].pop("table", None)
    repo.sources["SRC-04"]["provenance"].pop("asset", None)
    msgs = [v.message for v in schema.check_sources(repo)]
    assert any("names no asset" in m for m in msgs)
    assert any("dataset and table" in m for m in msgs)


def test_gate_deception_emitters_carry_their_own_placement(repo):
    # A deception estate spans assets, so placement sits per emitter.
    repo.sources["SRC-02"] = copy.deepcopy(repo.sources["SRC-02"])
    repo.sources["SRC-02"]["provenance"]["emitters"][0].pop("location", None)
    assert any("names no location" in v.message for v in schema.check_sources(repo))


def test_gate_untrusted_source_declares_sanitisation(repo):
    # The sanitiser refuses a document whose source declares no handling.
    repo.sources["SRC-01"] = copy.deepcopy(repo.sources["SRC-01"])
    repo.sources["SRC-01"]["provenance"]["handling"].pop("sanitisation", None)
    assert any("declares no sanitisation" in v.message for v in schema.check_sources(repo))


def test_gate_paid_source_declares_licensing(repo):
    # Redistribution terms surface in an audit, not in a build.
    repo.sources["SRC-03"] = copy.deepcopy(repo.sources["SRC-03"])
    repo.sources["SRC-03"]["provenance"].pop("licensing", None)
    assert any("no licensing terms" in v.message for v in schema.check_sources(repo))


def test_gate_campaign_observation_needs_tier(repo):
    repo.campaigns["CAMP-01"] = copy.deepcopy(repo.campaigns["CAMP-01"])
    repo.campaigns["CAMP-01"]["observations"][0].pop("source_tier", None)
    assert any("no source_tier" in v.message for v in schema.check_campaigns(repo))


def test_gate_public_overlap_must_say_what_it_changes(repo):
    # An external name is worth what it changes. An overlap entry that cannot
    # answer that is a name someone liked, not evidence.
    repo.campaigns["CAMP-01"] = copy.deepcopy(repo.campaigns["CAMP-01"])
    repo.campaigns["CAMP-01"]["public_overlap"][0].pop("would_change", None)
    assert any("would_change" in v.message for v in schema.check_campaigns(repo))


def test_gate_public_name_is_not_cluster_identity(repo):
    # The failure this guards: the vendor's evocative label quietly becoming the
    # campaign's own name, which is the conflation D-11 argues against.
    repo.campaigns["CAMP-01"] = copy.deepcopy(repo.campaigns["CAMP-01"])
    repo.campaigns["CAMP-01"]["name"] = "SLOW MANIFEST"
    assert any("cluster identity" in v.message for v in schema.check_campaigns(repo))


def test_gate_untrusted_agent_may_not_be_autonomous(repo):
    # The load-bearing gate. An agent that reads attacker-controlled text and is
    # allowed to self-merge is a persistence mechanism waiting to be driven.
    repo.agents["ttp-extractor"] = copy.deepcopy(repo.agents["ttp-extractor"])
    repo.agents["ttp-extractor"]["approval"] = "autonomous"
    assert repo.agents["ttp-extractor"]["untrusted_inputs"] is True
    assert any("autonomous" in v.message for v in schema.check_agents(repo))


def test_gate_evaluation_set_must_resolve(repo):
    # Declaring a path is not the same as creating one. An agent whose evaluation
    # set does not exist is an agent nobody is measuring.
    repo.agents["ttp-extractor"] = copy.deepcopy(repo.agents["ttp-extractor"])
    repo.agents["ttp-extractor"]["evaluation_set"] = "evals/does-not-exist/"
    assert any("does not resolve" in v.message for v in schema.check_agents(repo))


def test_gate_case_must_be_human_reviewed(repo):
    # If an agent can write its own precedent, the learning loop amplifies errors.
    repo.cases["CASE-0001"] = copy.deepcopy(repo.cases["CASE-0001"])
    repo.cases["CASE-0001"]["reviewer"] = None
    assert any("human-adjudicated" in v.message for v in schema.check_cases(repo))


def test_empty_tree_is_an_error_not_a_pass(tmp_path, capsys):
    """A validator that passes on nothing is worse than no validator.

    The trees load relative to the working directory unless a root is given, so
    running from the wrong place used to print "0 records, 0 violations" and exit
    zero. That is a green result that read nothing.
    """
    from ctiac import cli

    assert cli.main(["validate", str(tmp_path)]) == 2
    assert "no records found" in capsys.readouterr().err
    assert cli.main(["trace", str(tmp_path)]) == 2
    assert cli.main(["report", str(tmp_path)]) == 2


def test_gaps_lists_every_named_gap(capsys):
    """The gap listing is the collection plan's honest half. It must not drop one."""
    from ctiac import cli

    repo = load_repo(EXAMPLE)
    expected = sum(
        1
        for pir in repo.pirs.values()
        if pir.get("status") == "active"
        for e in pir.get("eei") or []
        if (e.get("gap") or "").strip()
    )
    assert expected, "the example should carry at least one named gap"
    assert cli.main(["gaps", str(EXAMPLE)]) == 0
    assert f"{expected} named gap(s)" in capsys.readouterr().out


# The remaining gates. Each constructs the forbidden shape once, so that every
# rule in schema.py has been watched failing at least once.


def test_gate_retired_pir_needs_reason(repo):
    repo.pirs["PIR-08"] = copy.deepcopy(repo.pirs["PIR-08"])
    repo.pirs["PIR-08"]["status"] = "retired"
    repo.pirs["PIR-08"]["retired_reason"] = None
    assert any("retired_reason" in v.message for v in schema.check_requirements(repo))


def test_gate_active_pir_needs_decision(repo):
    repo.pirs["PIR-08"] = copy.deepcopy(repo.pirs["PIR-08"])
    repo.pirs["PIR-08"]["decision"] = ""
    assert any("no decision" in v.message for v in schema.check_requirements(repo))


def test_gate_candidate_citing_retired_pir(repo):
    repo.pirs["PIR-03"] = copy.deepcopy(repo.pirs["PIR-03"])
    repo.pirs["PIR-03"]["status"] = "retired"
    repo.pirs["PIR-03"]["retired_reason"] = "test"
    assert any("not active" in v.message for v in schema.check_candidates(repo))


def test_gate_hunt_candidate_needs_hunt_ref(repo):
    repo.candidates["DC-07"] = copy.deepcopy(repo.candidates["DC-07"])
    repo.candidates["DC-07"]["origin"] = "hunt"
    repo.candidates["DC-07"]["hunt_ref"] = None
    assert any("hunt_ref" in v.message for v in schema.check_candidates(repo))


def test_gate_candidate_fixture_must_exist(repo):
    repo.candidates["DC-07"] = copy.deepcopy(repo.candidates["DC-07"])
    repo.candidates["DC-07"]["fixtures"]["true_positive"] = "fixtures/nope.json"
    repo.candidates["DC-07"]["fixtures"].pop("false_positive")
    msgs = [v.message for v in schema.check_candidates(repo)]
    assert any("fixture not found" in m for m in msgs)
    assert any("missing false_positive" in m for m in msgs)


def test_gate_decoy_pir_must_resolve(repo):
    repo.decoys["DEC-02"] = copy.deepcopy(repo.decoys["DEC-02"])
    repo.decoys["DEC-02"]["pir"] = "PIR-404"
    assert any("does not resolve" in v.message for v in schema.check_decoys(repo))


def test_gate_source_must_declare_class(repo):
    repo.sources["SRC-04"] = copy.deepcopy(repo.sources["SRC-04"])
    repo.sources["SRC-04"].pop("class")
    assert any("declares no class" in v.message for v in schema.check_sources(repo))


def test_gate_source_must_have_provenance(repo):
    repo.sources["SRC-04"] = copy.deepcopy(repo.sources["SRC-04"])
    repo.sources["SRC-04"].pop("provenance")
    assert any("no provenance" in v.message for v in schema.check_sources(repo))


def test_gate_external_source_names_transport_or_vendor(repo):
    repo.sources["SRC-01"] = copy.deepcopy(repo.sources["SRC-01"])
    repo.sources["SRC-01"]["provenance"].pop("origin")
    assert any("neither a transport nor a vendor" in v.message for v in schema.check_sources(repo))


def test_gate_merged_campaign_needs_merged_into(repo):
    repo.campaigns["CAMP-01"] = copy.deepcopy(repo.campaigns["CAMP-01"])
    repo.campaigns["CAMP-01"]["status"] = "merged"
    repo.campaigns["CAMP-01"]["merged_into"] = None
    assert any("merged_into" in v.message for v in schema.check_campaigns(repo))


def test_gate_campaign_pir_must_be_active(repo):
    repo.campaigns["CAMP-01"] = copy.deepcopy(repo.campaigns["CAMP-01"])
    repo.campaigns["CAMP-01"]["pirs"] = ["PIR-404"]
    assert any("active PIR" in v.message for v in schema.check_campaigns(repo))


def test_gate_agent_declares_blind_spots_and_eval_set(repo):
    repo.agents["ttp-extractor"] = copy.deepcopy(repo.agents["ttp-extractor"])
    repo.agents["ttp-extractor"]["blind_spots"] = []
    repo.agents["ttp-extractor"]["evaluation_set"] = None
    msgs = [v.message for v in schema.check_agents(repo)]
    assert any("blind_spots" in m for m in msgs)
    assert any("no evaluation_set" in m for m in msgs)
