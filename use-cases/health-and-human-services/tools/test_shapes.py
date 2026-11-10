#!/usr/bin/env python3
"""Negative tests: break each use case on purpose and confirm the shapes catch it.

Run tools/build.py first. Usage: python3 tools/test_shapes.py
"""
import pathlib, sys
import rdflib
from pyshacl import validate

HHS = pathlib.Path(__file__).resolve().parent.parent
P = """PREFIX ledger: <https://w3id.org/agent-ontology/ledger#>
PREFIX del: <https://w3id.org/agent-ontology/delegation#>
PREFIX ext: <https://example.org/sac-ucm-ext#>
PREFIX ucm: <https://www.w3.org/ns/ucm#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX hev: <http://w3id.org/holon/event/>
PREFIX acl: <http://www.w3.org/ns/auth/acl#>
PREFIX dcterms: <http://purl.org/dc/terms/>
"""
A, B, C, D = ("care-team-negotiated-join", "consent-scoped-sharing",
              "coordinator-handoff", "benefit-lapse-reinstatement")
# (case, what is broken, SPARQL update, text expected in the report)
TESTS = [
    (A, "Check 1: sub-delegation grants more than its parent",
     "INSERT { ?s del:allowedCapability <urn:test:extra> } WHERE { ?d del:delegationId 'A-D2' ; del:delegationScope ?s }", "Check 1"),
    (A, "Check 2: tampered hash breaks the chain",
     "DELETE { ?e ledger:hash ?h } INSERT { ?e ledger:hash 'sha256:tampered' } WHERE { ?e hev:eventSequence 3 ; ledger:hash ?h }", "Check 2"),
    (A, "Check 2: event signed with another agent's key",
     "DELETE { ?e ledger:publicKey ?k } INSERT { ?e ledger:publicKey 'did:example:someone-else#key-1' } WHERE { ?e hev:eventSequence 2 ; ledger:publicKey ?k }", "Check 2"),
    (A, "Handshake left pending but member admitted to team",
     "DELETE { ?h ucm:hasLifecycleState ucm:Accepted } INSERT { ?h ucm:hasLifecycleState ucm:Pending } WHERE { ?h a ucm:Handshake }", "Membership is negotiated"),
    (A, "Consent: the Pod's ACL rule names a different agent than the delegate",
     "DELETE { ?r acl:agent ?a } INSERT { ?r acl:agent <https://northgate.example/agents/coordination#agent> } WHERE { ?d del:delegationId 'A-D2' ; ext:consentRecord ?r . ?r acl:agent ?a }", "Consent missing"),
    (A, "Northgate's terms not enforced by any ACL rule",
     "DELETE { ?r dcterms:conformsTo ?p } WHERE { ?r dcterms:conformsTo ?p }", "enforced by an ACL rule"),
    (B, "Check 3: consent withdrawn in the Pod, but the diet-order write still admitted",
     "DELETE { ?r acl:mode acl:Append } WHERE { ?r acl:mode acl:Append ; acl:default <https://pod.example/delphine/holon/food-security/> }", "Check 3"),
    (B, "Check 3: therapy note request admitted instead of denied",
     "DELETE { ?e ext:verdict 'deny' } INSERT { ?e ext:verdict 'admit' } WHERE { ?e hev:eventSequence 5 }", "Check 3"),
    (B, "Consent limit: pantry admitted to the diagnosis",
     "DELETE { ?e ext:verdict 'deny' } INSERT { ?e ext:verdict 'admit' } WHERE { ?e hev:eventSequence 10 }", "pantry"),
    (C, "Check 4: sub-delegation left alive after its parent is revoked",
     "DELETE { ?e ?p ?o } WHERE { ?e hev:eventSequence 5 ; ?p ?o }", "Check 4: orphaned"),
    (C, "Check 3: stale coordinator authority admitted after revocation",
     "DELETE { ?e ext:verdict 'deny' } INSERT { ?e ext:verdict 'admit' } WHERE { ?e hev:eventSequence 10 }", "Check 3"),
    (C, "Consent stored outside Delphine's Pod",
     "DELETE { ?d ext:consentRecord ?r } INSERT { ?d ext:consentRecord <https://eastside-neighbors.example/acl#delphine> . <https://eastside-neighbors.example/acl#delphine> a acl:Authorization ; acl:agent ?to ; acl:mode acl:Read , acl:Write , acl:Append ; acl:default <https://pod.example/delphine/holon/discharge-coordination/> } WHERE { ?d del:delegationId 'C-D4' ; ext:consentRecord ?r ; del:delegatesTo ?to }", "Consent in the wrong place"),
    (C, "Coordination gap: successor starts a day late",
     "DELETE { ?p ucm:validFrom ?t } INSERT { ?p ucm:validFrom '2026-10-03T12:00:00Z'^^xsd:dateTime } WHERE { ?p ucm:validFrom ?t . FILTER(STRENDS(STR(?p), 'p-samuel-coordinator')) }", "Coordination gap"),
    (D, "Check 3: pickup admitted while the benefit is suspended",
     "DELETE { ?e ext:verdict 'deny' } INSERT { ?e ext:verdict 'admit' } WHERE { ?e hev:eventSequence 10 }", "Check 3"),
    (D, "Check 4: county tries to suspend a delegation it did not issue",
     "DELETE { ?e ledger:delegation ?d } INSERT { ?e ledger:delegation ?d4 } WHERE { ?e hev:eventSequence 9 ; ledger:delegation ?d . ?d4 del:delegationId 'D-D4' }", "Check 4: only the delegator"),
    (D, "Consent: Jules's Pod has no read rule for the county",
     "DELETE { ?r acl:mode acl:Read } WHERE { ?r acl:mode acl:Read ; acl:default <https://pod.example/jules/holon/income/> }", "Consent too narrow"),
    (D, "Lapse hidden: reinstatement missing from the record",
     "DELETE { ?e ledger:governanceAction ext:Reinstate } INSERT { ?e ledger:governanceAction ext:Grant } WHERE { ?e ledger:governanceAction ext:Reinstate }", "suspension in the record"),
]


def main():
    shared = rdflib.Graph().parse(HHS / "shared" / "four-checks.shacl.ttl")
    ext = rdflib.Graph().parse(HHS / "shared" / "sac-ucm-ext.ttl")
    failed = 0
    for case, what, update, expect in TESTS:
        g = rdflib.Graph().parse(HHS / case / f"{case}.ttl") + ext
        before = len(g)
        g.update(P + update)
        shapes = shared + rdflib.Graph().parse(HHS / case / f"{case}.shacl.ttl")
        conforms, _, report = validate(g, shacl_graph=shapes, advanced=True)
        caught = (not conforms) and expect in report
        changed = len(g) != before or "DELETE" in update
        print(f"{'CAUGHT' if caught else 'MISSED'}  {case}: {what}")
        if not caught or not changed:
            failed += 1
            print(report[:1500])
    print(f"\n{len(TESTS) - failed} of {len(TESTS)} deliberate breaks caught")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
