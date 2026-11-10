#!/usr/bin/env python3
"""Build and validate the health-and-human-services use cases.

For each case it joins tools/src/<case>.body.ttl with a ledger generated from
tools/src/<case>.ledger.tsv (real SHA-256 hash chain, placeholder signatures),
writes <case>.ttl and <case>.jsonld, converts the SHACL files to JSON-LD,
runs SHACL validation, and checks every term against the Agent Ontology and UCM.

Usage: python3 tools/build.py [--ontologies DIR_WITH_agent-ontology_AND_ucm]
Requires: rdflib, pyshacl.
"""
import argparse, hashlib, pathlib, sys
import rdflib
from rdflib import RDF, OWL, RDFS
from pyshacl import validate

HHS = pathlib.Path(__file__).resolve().parent.parent
SRC = HHS / "tools" / "src"
CASES = [c for c in ["care-team-negotiated-join", "consent-scoped-sharing",
         "coordinator-handoff", "benefit-lapse-reinstatement"] if (SRC / f"{c}.body.ttl").exists()]
CONTEXT = {
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#", "xsd": "http://www.w3.org/2001/XMLSchema#",
    "core": "https://w3id.org/agent-ontology/core#", "agent": "https://w3id.org/agent-ontology/agent#",
    "id": "https://w3id.org/agent-ontology/identity#", "del": "https://w3id.org/agent-ontology/delegation#",
    "cap": "https://w3id.org/agent-ontology/capability#", "intent": "https://w3id.org/agent-ontology/intent#",
    "ledger": "https://w3id.org/agent-ontology/ledger#", "sec": "https://w3id.org/agent-ontology/security-binding#",
    "ucm": "https://www.w3.org/ns/ucm#", "ext": "https://example.org/sac-ucm-ext#",
    "sh": "http://www.w3.org/ns/shacl#", "prov": "http://www.w3.org/ns/prov#",
    "acl": "http://www.w3.org/ns/auth/acl#", "holon": "http://w3id.org/holon/",
    "hev": "http://w3id.org/holon/event/", "dcterms": "http://purl.org/dc/terms/",
}


def ledger_ttl(case, body):
    """Turn the TSV rows into ledger events with a real hash chain."""
    did = {}
    g = rdflib.Graph().parse(data=body, format="turtle")
    for a, d in g.query("""PREFIX agent: <https://w3id.org/agent-ontology/agent#>
                           PREFIX id: <https://w3id.org/agent-ontology/identity#>
                           SELECT ?a ?d WHERE { ?a agent:hasIdentity/id:did ?d }"""):
        did[str(a)] = str(d)
    did = {curie: did[str(g.namespace_manager.expand_curie(curie))]
           for curie in {line.split("\t")[2] for line in (SRC / f"{case}.ledger.tsv").read_text().splitlines()
                         if line.strip() and not line.startswith("#")}}
    out, prev, n = ["\n##### Execution record: append-only, hash-chained, signed #####\n"], None, 0
    tag = "".join(w[0] for w in case.split("-")).upper()
    for line in (SRC / f"{case}.ledger.tsv").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        kind, time, actor, deleg, what, action, verdict, note = line.split("\t")
        n += 1
        eid = f"{tag}-{n:03d}"
        h = "sha256:" + hashlib.sha256("|".join(
            [prev or "", eid, did[actor], deleg, what, action, verdict, time]).encode()).hexdigest()
        t = [f"log:e{n:02d} a ledger:{'Governance' if kind == 'G' else 'Runtime'}LedgerEvent ; rdfs:label \"{note}\" ;",
             f"    ledger:eventId \"{eid}\" ; hev:eventSequence {n} ; ledger:appendOnly true ;"]
        if time != "-":
            t.append(f"    ledger:timestamp \"{time}\"^^xsd:dateTime ;")
        t.append(f"    ledger:actor {actor} ; ledger:delegation {deleg} ;")
        if kind == "G":
            t.append(f"    ledger:governanceAction ext:{what} ;")
        else:
            t.append(f"    ledger:usesCapability {what} ; ledger:action {action} ; ext:verdict \"{verdict}\" ;")
            t.append("    ledger:executionContext :gate ;")
        if prev:
            t.append(f"    ledger:previousEventHash \"{prev}\" ;")
        t.append(f"    ledger:hash \"{h}\" ;")
        t.append(f"    ledger:proofType \"DataIntegrityProof\" ; ledger:publicKey \"{did[actor]}#key-1\" ;")
        t.append(f"    ledger:signature \"placeholder-signature-{h[7:19]}\" .")
        out.append("\n".join(t))
        prev = h
    return "\n".join(out) + "\n"


def term_lint(data, onto_dir):
    """Report terms used in the data that neither ontology declares."""
    onto = rdflib.Graph()
    for f in list((onto_dir / "agent-ontology" / "ontologies").glob("*.ttl")) + \
            [onto_dir / "ucm" / "unified-care-model.ttl", HHS / "shared" / "sac-ucm-ext.ttl"]:
        onto.parse(f)
    declared = {s for s in onto.subjects(RDF.type, None)}
    used = set(data.predicates()) | set(data.objects(None, RDF.type)) | \
        {o for o in data.objects() if isinstance(o, rdflib.URIRef)}
    watch = ("https://w3id.org/agent-ontology/", "https://www.w3.org/ns/ucm#", "https://example.org/sac-ucm-ext#")
    return sorted(str(u) for u in used if str(u).startswith(watch) and u not in declared)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ontologies", type=pathlib.Path)
    args = ap.parse_args()
    prefixes = (SRC / "prefixes.ttl").read_text()
    shared = rdflib.Graph().parse(HHS / "shared" / "four-checks.shacl.ttl")
    ext = rdflib.Graph().parse(HHS / "shared" / "sac-ucm-ext.ttl")
    ok, undeclared = True, set()
    for case in CASES:
        body = prefixes + (SRC / f"{case}.body.ttl").read_text()
        ttl = body + ledger_ttl(case, body)
        d = HHS / case
        (d / f"{case}.ttl").write_text(ttl)
        data = rdflib.Graph().parse(data=ttl, format="turtle")
        (d / f"{case}.jsonld").write_text(data.serialize(format="json-ld", context=CONTEXT, indent=2) + "\n")
        own = rdflib.Graph().parse(d / f"{case}.shacl.ttl")
        (d / f"{case}.shacl.jsonld").write_text(own.serialize(format="json-ld", context=CONTEXT, indent=2) + "\n")
        conforms, _, report = validate(data + ext, shacl_graph=shared + own, advanced=True)
        print(f"{'PASS' if conforms else 'FAIL'}  {case}  ({len(data)} triples)")
        if not conforms:
            ok = False
            print(report)
        if args.ontologies:
            undeclared |= set(term_lint(data, args.ontologies))
    (HHS / "shared" / "four-checks.shacl.jsonld").write_text(
        shared.serialize(format="json-ld", context=CONTEXT, indent=2) + "\n")
    if args.ontologies:
        print("\nTerms used but not declared in the Agent Ontology or UCM:")
        for u in sorted(undeclared):
            print("  ", u)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
