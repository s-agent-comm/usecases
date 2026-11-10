# Benefit Lapse and Reinstatement

## Introduction

A county grocery benefit goes to Delphine's household. Five months in, a recertification notice goes to her old address, and the benefit is suspended on a day nobody can name. Her nephew is turned away at the pantry, the coordinator notices, pay stubs are sent, and the benefit is reinstated. This use case shows a suspension and reinstatement in the agents' record, ordered correctly even though one event has no timestamp.

Source: [UCM nutrition story](https://github.com/w3c-cg/ucm/blob/main/user-stories/care-team-coordination-nutrition.md), steps 6 to 11. All people, organizations and programs are fictional.

## User story

**As a** community health worker coordinating care (Samuel),
**I want** a lapse in the household's food benefit to be visible in the shared record as soon as it happens,
**so that** it is fixed before Delphine misses meals, and afterwards everyone can see what stopped, when in the sequence, and who restored it.

Supporting stories: Luis (county caseworker) wants household membership and income asserted once, with consent. Jules (caregiver) wants to know he counts as household for benefits but not as a patient.

## Key concepts illustrated

- **A group as a principal**: the household has its own Pod and locker agent.
- **Consent in each person's own Pod**: Delphine and Jules each grant the county a rule on their own container.
- **Separate consent chains**: Delphine and Jules each consent for their own data.
- **Suspend and reinstate**: governance events on one delegation.
- **Order without a timestamp**: the suspension has a position in the log and no clock time.
- **Suspension flows down the chain**: Jules's pickup is denied because the delegation above his is suspended.

## Workflow breakdown and ontology mapping

### 1. Two consents
- **Description**: Delphine consents to the county using her data for eligibility. Jules consents to the county reading his wages.
- **Ontology mapping**: `:d1` and `:d2`, each the root of its own `del:DelegationChain`. Jules's wages are a `ucm:SocialCareStatement`, not a new class.

### 2. Eligibility and grant
- **Description**: The county reads the wages, finds the household eligible, and grants the benefit to the household. The household lets Jules pick up.
- **Ontology mapping**: `core:Action`s under `:d2` and `:d1`; the result is a `ucm:SocialCareStatement` whose context is `definedByArtifact` the `EligibilityRuleset`. Benefit chain: `:d3` (county → household locker agent) and `:d4` (household agent → Jules's agent). `:d3` realizes Delphine's first `BeneficiaryRole` participation.
- **Why it matters**: the benefit is granted to a `Household`, so the household is the delegate. The income limit itself stays out of the graph.

### 3. A lapse
- **Description**: The recertification notice goes to the old address. The benefit is suspended; the exact day is unknown.
- **Ontology mapping**: a `ledger:GovernanceLedgerEvent` (suspend `:d3`) with no `ledger:timestamp`. Its position in the hash chain places it after the notice and before the next event. On the UCM side, the first participation gets a `validTo` and two `CareTrajectoryContext`s: after the recertification due date, before the coordinator notices.
- **Why it matters**: order survives a missing timestamp on both layers.

### 4. Turned away
- **Description**: Jules tries to pick up a box and is refused.
- **Ontology mapping**: a `ledger:RuntimeLedgerEvent` with verdict `deny`. Jules's own delegation `:d4` was never touched; the denial follows from the suspended `:d3` above it.

### 5. Reinstated
- **Description**: Jules sends pay stubs. The county reads them and reinstates the benefit. Pickups resume.
- **Ontology mapping**: an admitted read under `:d2`; a governance event (reinstate `:d3`); an admitted pickup. A second `BeneficiaryRole` participation opens with a `validFrom` equal to the reinstatement time.
- **Why it matters**: the agent side keeps one delegation through suspension and reinstatement. UCM has to close one participation and open another, because it gives lifecycle state only to processes. The case records both and flags the mismatch.

## Where the data and consent live

| What | Where |
| --- | --- |
| Jules's pay stubs | Jules's Pod, `holon/income/event.jsonld`; the county has a Read rule in `holon/income/.acl` |
| Eligibility result, benefit participations | Delphine's Pod, `holon/benefits/event.jsonld`; the county has a Read and Append rule in `holon/benefits/.acl` |
| The household | Its own WebID, `https://pod.example/arceneaux-household/profile/card.jsonld#us` |
| Execution record | The household's Pod, `holon/benefit-log/event.jsonld` |

The benefit chain (county → household → Jules) never touches a Pod, so it needs no consent record.

## The four checks

| Check | Result in this case |
| --- | --- |
| 1. Delegation-chain verifiability | Three chains, one root issuer each. `:d4` is within `:d3`. |
| 2. Execution-record integrity | Thirteen events, contiguous, each signed by its actor. One has no timestamp and is still placed by the chain. |
| 3. Authorization binding | The pickup during the lapse is denied and the pickup after reinstatement is admitted; both follow from the governance events before them. |
| 4. Accountability continuity | Suspension and reinstatement are both in the record, both made by the delegator (the county). A suspension by anyone else fails validation. |

## Files

- `benefit-lapse-reinstatement.ttl` / `.jsonld`: instance data
- `benefit-lapse-reinstatement.shacl.ttl` / `.shacl.jsonld`: case shapes (household is first-class; policy stays outside; the lapse is visible; order without a timestamp; trajectory positions)
- `../shared/four-checks.shacl.ttl`: the generic four checks
