# Handing Off the Coordinator Role

## Introduction

When Delphine goes home, the hospital steps back and a community health worker takes over coordination. The same people stay on the team in new roles. In agent terms, one delegation ends, another begins, and anything issued under the old one has to end with it. In Delphine's Solid Pod, the same handoff is a change to the access rules on her coordination record. This use case shows a handoff with no gap in coordination and no authority left behind.

Source: [UCM discharge story](https://github.com/w3c-cg/ucm/blob/main/user-stories/care-team-coordination-discharge.md), step 9. All people and organizations are fictional.

## User story

**As a** community health worker (Samuel, Eastside Neighbors),
**I want** a clean handoff of open tasks and coordinating authority when the hospital steps back,
**so that** nothing is dropped, and nobody keeps acting on authority that has ended.

Supporting story: Tomasz (Riverbend) wants to stay on the team for the 7-day follow-up call, and only that.

## Key concepts illustrated

- **Revocation as a recorded event**: a `ledger:GovernanceLedgerEvent`, issued by the delegator.
- **No orphaned authorization**: the sub-delegation Riverbend gave Harborlight is revoked with its parent.
- **Role and delegation move together**: each UCM `Participation` is tied to the delegation that realizes it.
- **Stale authority is refused**: two denied actions after the handoff.

## Workflow breakdown and ontology mapping

### 1. Before discharge
- **Description**: Riverbend coordinates. It has brought Harborlight in for housing tasks.
- **Ontology mapping**: `:d1` (Delphine → Riverbend: coordinate, housing tasks, follow-up) realizes Tomasz's `CoordinatorRole` participation. `:d2` (Riverbend → Harborlight: housing tasks).

### 2. Handoff note
- **Description**: Riverbend's agent writes the open tasks down for the next coordinator.
- **Ontology mapping**: a `core:Action` producing a `ucm:CareCoordinationStatement`, the last act under `:d1`.

### 3. The handoff
- **Description**: At discharge, four things happen at one moment. Riverbend withdraws what it gave Harborlight. Delphine's locker agent ends Riverbend's coordinator authority, grants Riverbend follow-up only, and grants Eastside coordination. In the Pod, two rules leave `discharge-coordination/.acl`, one is added there for Eastside, and one is added to `clinical/.acl` for Riverbend's follow-up.
- **Ontology mapping**: governance events: revoke `:d2`, revoke `:d1`, grant `:d3` (follow-up; realizes Tomasz's `ProviderRole` participation), grant `:d4` (coordinate; realizes Samuel's `CoordinatorRole` participation). Tomasz's coordinator participation gets a `validTo`; Samuel's `validFrom` is the same instant.
- **Why it matters**: "same people, new roles" is visible on both layers, and the times agree.

### 4. Eastside re-issues Harborlight's authority
- **Description**: Harborlight still has housing tasks to finish, now for the new coordinator.
- **Ontology mapping**: `:d5` (Eastside → Harborlight: housing tasks).

### 5. After the handoff
- **Description**: Riverbend's agent tries to send a new coordination request and is refused. Harborlight's agent tries its old Riverbend authority and is refused, then succeeds under Eastside's. Riverbend records the follow-up call.
- **Ontology mapping**: four `ledger:RuntimeLedgerEvent`s: `deny`, `deny`, `admit`, `admit`.

## Where the data and consent live

| What | Where in Delphine's Pod |
| --- | --- |
| Coordination record, handoff note, task updates | `holon/discharge-coordination/event.jsonld` |
| Follow-up call note | `holon/clinical/event.jsonld` |
| Consent before the handoff | `discharge-coordination/.acl`: Riverbend (coordinator), Harborlight (via Riverbend) |
| Consent after the handoff | `discharge-coordination/.acl`: Eastside (coordinator), Harborlight (via Eastside); `clinical/.acl`: Riverbend (follow-up) |
| Execution record | `holon/access-log/event.jsonld` |

The `.acl` shows only the current rules. The governance events in the access log are the history: without them, nothing in the Pod would show that Riverbend was ever coordinator.

## The four checks

| Check | Result in this case |
| --- | --- |
| 1. Delegation-chain verifiability | One root issuer. `:d2` is within `:d1`; `:d5` is within `:d4`. |
| 2. Execution-record integrity | Thirteen events, contiguous, each signed by its actor. |
| 3. Authorization binding | Two actions on revoked authority are denied; the verdict follows from the revocation events earlier in the log. |
| 4. Accountability continuity | Each revocation is made by the delegator. Removing the revocation of `:d2` fails validation as an orphaned authorization. Both revoked delegations carry an end date. |

## Files

- `coordinator-handoff.ttl` / `.jsonld`: instance data
- `coordinator-handoff.shacl.ttl` / `.shacl.jsonld`: case shapes (role and delegation start and end together; no coordinator gap or overlap; roles live on participations)
- `../shared/four-checks.shacl.ttl`: the generic four checks
