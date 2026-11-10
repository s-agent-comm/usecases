# Sharing Data Within the Limits of Consent

## Introduction

Two parties on Delphine's care team need something from her record, and neither should see all of it. The hospital needs to know her counseling is on track, without reading therapy notes. The food pantry needs her diet type, without seeing a diagnosis. Her data sits in separate containers in her Solid Pod, and each consent is an access rule on one container. The Pod server admits or denies each request, and both outcomes are recorded in her Pod.

Sources: [UCM discharge story](https://github.com/w3c-cg/ucm/blob/main/user-stories/care-team-coordination-discharge.md), step 5; [UCM nutrition story](https://github.com/w3c-cg/ucm/blob/main/user-stories/care-team-coordination-nutrition.md), steps 5 and 9. All people and organizations are fictional.

## User story

**As a** person receiving care (Delphine),
**I want** my agent to release each statement only to parties I have consented to, and only from contexts I have agreed to share,
**so that** my counselor and the pantry can coordinate my care without my therapy notes or diagnosis travelling further than I intended.

Supporting stories: Priya (counselor) wants to join the team without exposing therapy notes. Margit (pantry lead) wants only the diet type and pickup details.

## Key concepts illustrated

- **Context as an authorization input**: every UCM `Statement` is `madeWithinContext`; each capability names the contexts it may touch.
- **Capability constraint**: `cap:allowedContext` and `cap:prohibitedContext` carry the consent limit.
- **Sub-delegation**: Riverbend passes the pantry one capability.
- **Denied actions are recorded**: three denials, each with a reproducible reason.
- **Consent as container layout**: WAC grants access per container, so each limit is also a choice of where a statement is stored.
- **Authorization binding**: the verdict is a function of the record and the Pod's ACL rules.

## Workflow breakdown and ontology mapping

### 1. Two consents
- **Description**: Delphine consents to Northgate holding her notes and sharing a summary, and to Riverbend's care team reading clinical and coordination statements. Behavioral health is not in Riverbend's grant.
- **Ontology mapping**: `del:Delegation`s `:d1` (Northgate) and `:d2` (Riverbend), each with its own `del:DelegationScope`. Their consent records are ACL rules: Northgate on `behavioral-health/` (Read, Write) and `care-coordination/` (Append); Riverbend on `clinical/` (Read), `care-coordination/` and `food-security/` (Read, Append). Riverbend has no rule on `behavioral-health/`.
- **Why it matters**: consent is per party and per capability, not one switch.

### 2. A summary crosses the boundary; the note does not
- **Description**: Northgate's agent writes a coordination summary. Riverbend's agent reads it. Riverbend's agent then asks for the session note and is refused, twice: once using its coordination capability (wrong context), once naming a behavioral health capability it was never given.
- **Ontology mapping**: the summary is a `ucm:CareCoordinationStatement` in the `SocialCareContext`; the note is a `ucm:ClinicalStatement` in the `BehavioralHealthContext`. Four `ledger:RuntimeLedgerEvent`s: two `admit`, two `deny`.
- **Why it matters**: the UCM acceptance criterion "no `ClinicalStatement` from the `BehavioralHealthContext` is exposed outside it" becomes a testable property of the record.

### 3. The diet order reaches the pantry
- **Description**: Riverbend's dietitian records a diet recommendation as a coordination statement. The diet order is stored in `food-security/`, the one container the pantry will be allowed to read. Riverbend passes the pantry agent permission to read coordination statements, and Delphine's locker agent adds the pantry's rule on that container only. The pantry reads the diet type. It then asks for the diagnosis and is refused.
- **Ontology mapping**: sub-delegation `:d3` with one capability; `ucm:PolicyDefinition` `:pantryTerms`; two more runtime events, one `admit` and one `deny`.
- **Why it matters**: the pantry can serve Delphine without holding her medical record, and can show that it never did.

## Where the data and consent live

| Container in Delphine's Pod | Holds | ACL rules |
| --- | --- | --- |
| `holon/behavioral-health/` | Therapy notes | Northgate (Read, Write) |
| `holon/clinical/` | Diagnoses | Riverbend (Read) |
| `holon/care-coordination/` | Coordination summaries | Riverbend (Read, Append); Northgate (Append) |
| `holon/food-security/` | The diet order | Riverbend (Read, Append); the pantry (Read) |
| `holon/access-log/` | The execution record | |

## The four checks

| Check | Result in this case |
| --- | --- |
| 1. Delegation-chain verifiability | One root issuer. `:d3` grants a subset of `:d2`. |
| 2. Execution-record integrity | Ten events, contiguous, each signed by its actor. |
| 3. Authorization binding | Seven gated actions: four admitted, three denied. Each verdict is recomputed from actor, capability, delegation state, the target statement's context and the ACL rule on its container. The therapy note and the diagnosis are refused on two grounds: wrong context, and no rule for that agent on that container. Changing any deny to admit fails validation. |
| 4. Accountability continuity | Three grants, each by the delegator. |

## Files

- `consent-scoped-sharing.ttl` / `.jsonld`: instance data
- `consent-scoped-sharing.shacl.ttl` / `.shacl.jsonld`: case shapes (statements carry context; behavioral health stays in context; the pantry sees only Social Care statements; denials are on record; each policy is enforced by an ACL rule)
- `../shared/four-checks.shacl.ttl`: the generic four checks
