# Joining a Care Team by Agreement

## Introduction

A hospital asks a housing agency and a behavioral health clinic to help with one person's discharge. Nobody is added to her care team by assumption. Each organization's agent is asked, and each answers, and one of them answers with conditions. This use case models that negotiation between agents, and shows that every team member's presence can be traced to the person's own consent.

Source: [UCM discharge story](https://github.com/w3c-cg/ucm/blob/main/user-stories/care-team-coordination-discharge.md), steps 2 to 6. All people and organizations are fictional.

## User story

**As a** care transitions coordinator (Tomasz, Riverbend General Hospital),
**I want** my agent to form a cross-domain care team in which each member joins by agreement, on its own stated terms,
**so that** Delphine leaves the hospital with housing and behavioral health support in place, and anyone can later verify why each party was on her team.

## Key concepts illustrated

- **Agent identity**: four agents, each with a WebID, a DID, and a principal named by `prov:actedOnBehalfOf`.
- **Delegation chain**: Delphine's locker agent → Riverbend → Harborlight and Northgate.
- **Consent in the Pod**: each delegation is put into effect by a rule in the discharge-coordination container's `.acl`.
- **Attenuation**: Riverbend passes each partner one capability out of the four it holds.
- **Capability constraint**: Northgate's acceptance is bound to a UCM `PolicyDefinition`, and its ACL rule cites that policy.
- **Intent**: one intent, authorized by the root delegation, produces the requests.
- **Execution record**: eight signed, hash-chained events.

## Workflow breakdown and ontology mapping

### 1. Delphine consents to coordination
- **Description**: A screening shows Delphine's lease ends in three weeks. She agrees that Riverbend may coordinate her discharge.
- **Ontology mapping**: `del:Delegation` `:d1` from Delphine's locker agent to Riverbend's agent, put into effect by the `acl:Authorization` `discharge-coordination/.acl#riverbend` (Read, Write, Append), with a `del:DelegationScope` of four capabilities, an `intentConstraint`, and a validity window. Recorded as a `ledger:GovernanceLedgerEvent` (grant). On the UCM side, a `CareCoordinationInteraction` with an `ActivityFocus`.
- **Why it matters**: this is the root of the chain. Everything later is checked against it.

### 2. Matching identity
- **Description**: Harborlight already knows Delphine as "D. Arceneaux". Riverbend's agent writes a match claim into Delphine's Pod: Harborlight's record is the person identified by her WebID.
- **Ontology mapping**: a `core:Action` that `producesArtifact` a `ucm:MatchClaim`, under capability `:capAssertMatch`.
- **Why it matters**: no second `Person` is created, and the claim has an accountable author.

### 3. Asking for help
- **Description**: Riverbend's agent writes a request to Harborlight and one to Northgate into Delphine's Pod, each with an offer of narrowed authority. Riverbend cannot change Delphine's `.acl` itself, so her locker agent adds a rule for each partner at Riverbend's request.
- **Ontology mapping**: two `core:Action`s producing `ucm:CoordinationRequest`s; sub-delegations `:d2` (housing referral only) and `:d3` (summary sharing only).
- **Why it matters**: the partner sees exactly what it is being asked to do before it answers.

### 4. Agreeing to participate
- **Description**: Harborlight accepts as is. Northgate accepts on terms: therapy notes stay inside the Behavioral Health context, and only a coordination summary is shared.
- **Ontology mapping**: each acceptance is a `core:Action` producing a `ucm:Handshake` with `hasLifecycleState ucm:Accepted`. Northgate's terms are a `ucm:PolicyDefinition`, bound to `:capShareSummary` by a `cap:CapabilityConstraint` (`allowedContext`, `prohibitedContext`, `requiresPermission`).
- **Why it matters**: the accepting party sets a limit, and the limit is machine-readable on the capability it will use.

### 5. The care team forms
- **Description**: The team now has Delphine, Tomasz, Amara and Priya.
- **Ontology mapping**: `ucm:CareTeam`, `Membership`, `MembershipCriteria`. A case shape requires that each invited member's organization accepted a handshake.
- **Why it matters**: membership is a consequence of recorded agreement, not a list someone typed.

## Where the data and consent live

| What | Where in Delphine's Pod |
| --- | --- |
| Delphine | Her WebID, `https://pod.example/delphine/profile/card.jsonld#me` |
| Coordination, requests, handshakes, team, match claim | `holon/discharge-coordination/event.jsonld` |
| Contexts, roles, Northgate's terms | `holon/discharge-coordination/boundary.jsonld` |
| Consent for Riverbend, Harborlight and Northgate | `holon/discharge-coordination/.acl` |
| Execution record | `holon/access-log/event.jsonld` |

## The four checks

| Check | Result in this case |
| --- | --- |
| 1. Delegation-chain verifiability | One root issuer (Delphine's locker agent). `:d2` and `:d3` each grant a subset of `:d1`. Each delegation has its ACL rule in Delphine's Pod. |
| 2. Execution-record integrity | Eight events, contiguous, each signed by its actor. |
| 3. Authorization binding | All five gated actions are admitted, and each verdict is recomputed from delegation, scope, state and the ACL rule covering the written resource. |
| 4. Accountability continuity | Three grants, each by the delegator. No revocation occurs in this case. |

## Files

- `care-team-negotiated-join.ttl` / `.jsonld`: instance data
- `care-team-negotiated-join.shacl.ttl` / `.shacl.jsonld`: case shapes (accepted handshakes, negotiated membership, match claim, consent terms in use)
- `../shared/four-checks.shacl.ttl`: the generic four checks
