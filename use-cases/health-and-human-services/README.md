# Use cases: care coordination with consent-enforcing agents

Four use cases for the Semantic Agent Communication CG, drawn from the two Unified Care Model (UCM) user stories:

- [Care Team Coordination: A Patient Discharge Home](https://github.com/w3c-cg/ucm/blob/main/user-stories/care-team-coordination-discharge.md)
- [Care Team Coordination: Nutrition Assistance](https://github.com/w3c-cg/ucm/blob/main/user-stories/care-team-coordination-nutrition.md)

The UCM stories describe people and organizations. These use cases add one layer: each party has a software agent that acts for it, and each story step becomes an exchange between agents. UCM terms describe **what** is exchanged (persons, roles, statements, contexts). Agent Ontology terms describe **who may do what, on whose authority, and what was recorded**.

The personal data and the consent both come from the person's own Solid Pod, set up as in [personal-data-locker](https://github.com/alexandria-consulting/personal-data-locker) (see [Where data and consent come from](#where-data-and-consent-come-from)).

They form a new `health-and-human-services` category and follow the layout of the other categories in this repository. All people, organizations and programs are fictional.

Status: draft for discussion. Not adopted by either Community Group.

## The four use cases

| | Use case | Story steps | What it shows |
| --- | --- | --- | --- |
| A | [Joining a care team by agreement](care-team-negotiated-join/) | Discharge 2–6 | A `CoordinationRequest` and `Handshake` between agents identified by WebID and DID, written into Delphine's Pod; a sub-delegation narrowed to the accepting party's own terms; a `MatchClaim` so no second person is created. |
| B | [Sharing data within the limits of consent](consent-scoped-sharing/) | Discharge 5; Nutrition 5, 9 | Therapy notes stay in their own Pod container; the pantry's ACL rule covers only the container holding the diet order. Denied requests are on the record, and every verdict can be recomputed. |
| C | [Handing off the coordinator role](coordinator-handoff/) | Discharge 9 | The coordinator role moves from the hospital to a community health worker with no gap, no overlap and no leftover authority, by changing the rules in the Pod's `.acl`. |
| D | [Benefit lapse and reinstatement](benefit-lapse-reinstatement/) | Nutrition 6–11 | A benefit is suspended on an unknown day and later reinstated. The record still orders the events and denies a pickup during the lapse. |

## Agents

| Agent | Acts on behalf of | Cases |
| --- | --- | --- |
| Delphine's locker agent | Delphine Arceneaux (`ucm:Person`, her WebID) | A, B, C, D |
| Jules's locker agent | Jules Arceneaux (`ucm:Person`, his WebID) | D |
| Household locker agent | Delphine and Jules's grocery unit (`ucm:Household`, its WebID) | D |
| Riverbend agent | Riverbend General Hospital (`ucm:Organization`) | A, B, C |
| Harborlight agent | Harborlight Housing Collaborative (`ucm:Organization`) | A, C |
| Northgate agent | Northgate Community Mental Health (`ucm:Organization`) | A, B |
| Eastside agents | Eastside Neighbors and its pantry (`ucm:CommunityGroup`) | B, C |
| County agent | Bramble County DHS (`ucm:Organization`) | D |

Each agent is identified by an https WebID, so a Pod's access rules can name it, and also has a `did:web` DID for signing the record. Each names its principal with `prov:actedOnBehalfOf`, as the locker agent does in personal-data-locker.

## Where data and consent come from

Delphine, Jules and their household each have a Solid Pod on a JSS server (`https://pod.example/` stands in for one), laid out as in personal-data-locker:

| Pod element | How the use cases use it |
| --- | --- |
| WebID `…/profile/card.jsonld#me` | The person's `ucm:Person`. Every UCM participation and statement about Delphine points at her WebID, so there is never a second Delphine. |
| Holon containers under `…/holon/` | The personal data. Each holon (an `AgentHolon` for the locker, `DataHolon`s and `ProcessHolon`s inside it) is a container with scene, boundary, event and projection graphs. Statements live in a holon's `event.jsonld`; contexts, policies and roles in its `boundary.jsonld`. |
| A container's `.acl` (Web Access Control, JSON-LD) | The consent. Each `acl:Authorization` names an agent's WebID, a container and access modes. Every delegation that touches Pod data points at its rule with `ext:consentRecord`. |
| The locker agent | Writes the `.acl` rules. Only the Pod owner holds `acl:Control`, so even a sub-delegation (Riverbend inviting the pantry) is put into effect by Delphine's locker agent. |
| `…/holon/access-log/event.jsonld` | The execution record of cases A to C, kept in Delphine's own Pod. Case D's is in the household's Pod. Events carry `hev:eventSequence`, as holon events do. |

The containers used are:

| Pod | Container | Holds | Who has a rule on it |
| --- | --- | --- | --- |
| Delphine | `holon/discharge-coordination/` | Requests, handshakes, team, match claim, handoff note | Riverbend, then Eastside; Harborlight; Northgate |
| Delphine | `holon/behavioral-health/` | Therapy notes | Northgate only |
| Delphine | `holon/clinical/` | Diagnoses, follow-up notes | Riverbend |
| Delphine | `holon/care-coordination/` | Coordination summaries | Riverbend; Northgate (append) |
| Delphine | `holon/food-security/` | The diet order for the pantry | Riverbend; the pantry (read) |
| Delphine | `holon/benefits/` | Eligibility result, benefit participations | The county |
| Jules | `holon/income/` | Pay stubs | The county (read) |

An action is an HTTP request against one of these. It reads a resource (`prov:used`) or writes one (`core:producesArtifact`), and check 3 recomputes the verdict from the delegation and its ACL rule.

## From story step to agent exchange

| Story step | Agents | UCM terms | Agent Ontology terms | Case |
| --- | --- | --- | --- | --- |
| Discharge 2. A social need surfaces; coordination opens | Delphine → Riverbend | `CareCoordinationInteraction`, `ActivityFocus` | `del:Delegation` (root, Delphine's consent), `intent:Intent` | A |
| Discharge 3. Matching identity | Riverbend | `MatchClaim` | `core:Action`, `core:Artifact`, `id:did` | A |
| Discharge 4. Asking for help | Riverbend → Harborlight, Northgate | `CoordinationRequest` | `core:Action`, sub-`del:Delegation` | A |
| Discharge 5. Agreeing to participate, on terms | Harborlight, Northgate | `Handshake`, `acceptsRequest`, `PolicyDefinition` | `cap:CapabilityConstraint`, `del:DelegationScope` | A, B |
| Discharge 6. The care team forms | all | `CareTeam`, `Membership`, `MembershipCriteria` | `del:DelegationChain` | A |
| Discharge 9. Discharge and handoff | Delphine, Riverbend, Eastside, Harborlight | `Participation` `validFrom` / `validTo`, `CoordinatorRole`, `ProviderRole` | `ledger:GovernanceLedgerEvent` (grant, revoke) | C |
| Nutrition 5. Pantry accepts with a data limit | Riverbend → pantry | `PolicyDefinition`, `SocialCareContext` | `cap:allowedContext`, `cap:prohibitedContext` | B |
| Nutrition 7–8. Household eligibility | Delphine, Jules → county | `Household`, `EligibilityDetermination`, `EligibilityRuleset`, `SocialCareStatement` | two consent `del:DelegationChain`s, `core:Action` | D |
| Nutrition 9. Diet order reaches the pantry | Riverbend, pantry | `CareCoordinationStatement` | `ledger:RuntimeLedgerEvent` with a verdict | B |
| Nutrition 10. A lapse | county | `Participation` `validTo`, `CareTrajectoryContext` | governance event (suspend) with no timestamp | D |
| Nutrition 11. Reinstated | Jules, county, household | new `Participation` `validFrom` | governance event (reinstate) | D |

Story steps that involve no exchange between parties (admission, the housing assessment itself, home monitoring readings) are left to the UCM stories.

## The four checks

Each case is tested against the four checks Xinghua Zhao proposed on the CG list on 6 November 2026 (an individual contribution, not adopted). [`shared/four-checks.shacl.ttl`](shared/four-checks.shacl.ttl) states them as SHACL shapes over Agent Ontology terms.

| Check | What the shapes require | Best shown in |
| --- | --- | --- |
| 1. Delegation-chain verifiability | Every agent has a WebID, a DID and a principal. Every delegation that grants Pod access has a consent record: an ACL rule in the root person's Pod, naming the delegate, with every access mode its capabilities need. Each chain has one root issuer. A sub-delegation never grants a capability its parent did not. Every delegation is granted by a signed event. | A |
| 2. Execution-record integrity | Every event has an id, a position, a hash, and a signature made with a key of its own actor's DID. Each `previousEventHash` equals the hash one position earlier. No forks. | all |
| 3. Authorization binding | Every gated action records a verdict. `admit` is recomputed from the record alone: the actor is the delegate, the capability is in scope, no delegation on the path is revoked or suspended, the target statement's UCM context is one the capability allows, and the delegation's ACL rule grants the actor the needed mode on a container holding the target. Any mismatch is a violation. | B |
| 4. Accountability continuity | Only the delegator may grant, revoke, suspend or reinstate. Revoking a delegation requires revoking the sub-delegations under it. A revoked delegation carries an end date. | C, D |

The hash chain is real (SHA-256 over each event's fields and the previous hash). Signatures are placeholders: no keys exist for the fictional DIDs.

## Gaps found

Writing the cases exposed places where the two ontologies do not yet meet, or where the Agent Ontology cannot say what the checks need.

**Bridging terms that had to be proposed** ([`shared/sac-ucm-ext.ttl`](shared/sac-ucm-ext.ttl), namespace `https://example.org/sac-ucm-ext#`):

| Proposed term | Gap it fills |
| --- | --- |
| `ext:consentRecord` | Nothing links a delegation to the access rule that puts it into effect. Here it points from each delegation to the `acl:Authorization` in the person's Pod. |
| `ext:verdict` | No term records the gate's admit or deny decision. `ledger:result` points to `core:ExecutionResult`, which is not declared. Check 3 needs the verdict. |
| `ext:Grant`, `ext:Revoke`, `ext:Suspend`, `ext:Reinstate` | `ledger:governanceAction` has range `ledger:GovernanceAction`, which is not declared and has no members. Check 4 needs these four at least. |
| `ext:realizesParticipation` | Nothing links a delegation to the UCM role participation it puts into effect. Cases C and D compare the two lifecycles. |

Moving to the Pod model removed three bridging terms an earlier draft needed, because the Pod's vocabularies already have them: `prov:actedOnBehalfOf` for an agent's principal (the Agent Ontology's `agent:owner` is a string), `prov:used` for the resource an action read, and `hev:eventSequence` for an event's position when its time is unknown. The Agent Ontology could reuse all three.

**Solid and Web Access Control**

- WAC has no delegation. Only the Pod owner holds `acl:Control`, and a rule names one agent with no record of who asked for it. When Riverbend invites the pantry, Delphine's locker agent writes the rule; the chain from Delphine through Riverbend exists only in the agent layer.
- WAC has no history. A `.acl` holds the current rules, and a revoked rule simply disappears. The governance events in the access log are what show that Riverbend once coordinated and then stopped. This matches personal-data-locker's own pattern: the `.acl` is like a scene graph, and the log is its event graph.
- WAC grants access per container, not per statement. Each consent limit therefore becomes a choice of where data lives: the diet order goes in `food-security/` so that the pantry can read it without reading the coordination summaries.
- A rule cannot say which policy it enforces. The cases add `dcterms:conformsTo` from the rule to the `ucm:PolicyDefinition`. JSS may not keep extra triples in a `.acl`; this was not tested against a running server.
- WAC rules name WebIDs and the Agent Ontology names DIDs. Each agent here has both, with nothing that formally ties them together.

**Agent Ontology**

- `cap:allowedContext`, `cap:prohibitedContext` and `cap:requiresPermission` are strings. The cases put IRIs of UCM contexts and WAC access modes in them. Object properties would let them be followed and validated.
- `ledger:actor`, `acc:actor` and `sec:hasKeyMaterial` point to `agent:Agent`, which is not declared. `core:Agent` is. The cases use `core:Agent`.
- `ledger:result` points to `core:ExecutionResult` and `sec:signsRecord` to `ledger:LedgerRecord`; neither class is declared. `intent:loggedAs` points to `ledger:RuntimeLedgerRecord`, while the class is `ledger:RuntimeLedgerEvent`.
- `core:Delegation` and `del:Delegation` each define `delegatedBy`, `delegatesTo` and `delegationScope`, with different ranges for scope. The cases use the `del:` terms.
- Revocation has no home. `del:validUntil` is on the scope, and nothing says who ended a delegation or why.
- The other examples in this repository use the `https://ns.slashlife.ai/agent/` namespace. These cases use `https://w3id.org/agent-ontology/`.

**UCM** (in addition to the gaps the two stories already list)

- A `PolicyDefinition` has no machine-readable content. The consent limit lives in the capability constraint on the agent side, with only an IRI pointing back to the policy.
- UCM has no consent or authorization class. Here consent is a WAC rule in the Pod, and UCM only names the policy it enforces.
- `hasLifecycleState` applies to processes, and the vocabulary has Pending, Accepted and Declined. Case C needs "handed off"; case D needs Suspended and Reinstated on a participation. The agent side can say suspend and reinstate on one delegation; UCM has to close one participation and open another.
- `hasCareTrajectoryContext` has no domain or range, and a `CareTrajectoryContext` cannot say "after X" or "before Y" except in its label.

## Files

```
shared/
  four-checks.shacl.ttl      generic shapes for the four checks (+ .jsonld)
  sac-ucm-ext.ttl            proposed bridging terms
<use-case>/
  README.md                  user story, concepts, workflow, mapping
  <use-case>.ttl             instance data (+ .jsonld)
  <use-case>.shacl.ttl       case-specific shapes (+ .jsonld)
tools/
  build.py                   builds the data files and validates them
  test_shapes.py             breaks each case on purpose and confirms the shapes catch it
  src/                       hand-written sources: <use-case>.body.ttl and <use-case>.ledger.tsv
```

The `.ttl` and `.jsonld` data files are generated. Edit `tools/src/` and rebuild.

## Build and validate

```bash
pip install rdflib pyshacl
cd use-cases/health-and-human-services
python3 tools/build.py          # 4 of 4 cases conform
python3 tools/test_shapes.py    # 17 of 17 deliberate breaks caught
```

To also check that every term is declared, clone `s-agent-comm/agent-ontology` and `w3c-cg/ucm` side by side into one directory and pass it: `python3 tools/build.py --ontologies <dir>`.
