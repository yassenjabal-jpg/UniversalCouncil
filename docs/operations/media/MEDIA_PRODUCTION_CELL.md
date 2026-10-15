# Media Production Cell v1.5

Status: CANONICAL MEDIA OPERATIONS
Date: 2026-10-15

Governing config:
`company/config/media_venture.json`

Master workflow:
`STUDIO_MASTER_PIPELINE.md`

## Operating model

The Studio uses a three-phase project architecture:

1. **Writing**
2. **Pre-production**
3. **Production**

Only the Media Producer remains always active as a non-craft control plane.

All creative/editorial functions are activated only inside the phase or production department that owns their work.

The Independent Fact Checker remains an independent clearance function.

Human Assistance remains an on-demand bounded exception.

## Writing

Writing has two sections.

### Market & Title Development

The project starts from market and audience evidence, not from a preselected script idea.

Required:
- read YouTube demand;
- read social/platform trends;
- synthesize a market opportunity;
- verify evidence, visual and eight-minute story feasibility;
- produce **exactly three** title candidates;
- present all three to the Owner.

The Owner selects one.

No script work starts before:
**OWNER_TITLE_LOCK**

The Studio may later propose a title refinement, but the title cannot change without explicit Owner reapproval.

### Script Development

After Owner Title Lock:

S0 Story Question  
S1 Research Pack  
S2 Story Architecture  
S3 First Script  
S4 Editorial Rewrite  
S5 Independent Fact Check  
S6 Narration Rewrite  
S7 Locked Script

Writing exits only at:
**SCRIPT_LOCK**

## Pre-production

Pre-production begins only after Script Lock.

Its job is to transform the script into a complete manufacturing plan.

It owns:
- script breakdown;
- Visual Story Case;
- art direction;
- asset plan;
- rights/source preclearance;
- shot design;
- storyboard;
- camera and continuity plan;
- sonic concept;
- narration plan;
- title-promise alignment;
- animatic;
- Production Readiness Review.

It exits only at:
**PRODUCTION_READY_LOCK**

A script problem returns to Writing through a formal return ticket.

A title/story mismatch creates an Owner title-revision request; it never silently changes the title.

## Production

Official production mode:

**SERIAL PRODUCTION LINE WITH FEEDBACK GATES**

Only one craft department may be active on the project at a time.

Each department:
1. receives an accepted input packet;
2. completes its internal stages in order;
3. uses exactly one primary program per stage;
4. verifies its output;
5. checkpoints;
6. issues a handoff packet;
7. waits for acceptance before the next department starts.

Production departments:

1. Voice & Narration
2. Visual Asset Production
3. Motion & Compositing
4. Picture Editing
5. Sound Design & Mix
6. Thumbnail & Packaging
7. Assurance & Delivery
8. Learning & Archive

The exact stage/program map is defined in:
`STUDIO_MASTER_PIPELINE.md`

## Feedback rule

A downstream department may not silently repair locked upstream work.

If it finds a defect:
- issue a Return Ticket;
- identify the source department;
- identify the artifact and defect;
- state the requested correction;
- state what must not change;
- return the work to the source department.

The source department repairs and reissues its handoff.

## One Program Per Stage

Every stage has one named primary program.

A second simultaneous craft program is forbidden.

Changing the primary program requires:
- closing/checkpointing the current stage;
- opening a new stage or recovery stage.

## Control plane

The Media Producer may:
- open and close stages;
- manage schedule/dependencies;
- validate handoffs;
- trigger recovery;
- coordinate bounded Human Assistance;
- preserve checkpoints and delivery state.

The Producer does not edit craft artifacts.

## Core authority boundaries

Owner:
- final title selection;
- title revision approval after lock;
- voice/performance approval where required;
- brand authority;
- public publish approval;
- credentials, spend, subscriptions and irreversible external actions.

Showrunner:
- story architecture;
- script quality;
- editorial coherence;
- editorial approval.

Independent Fact Checker:
- material factual clearance.

Craft departments:
- own their stage outputs;
- may not self-approve an independent clearance they do not own.

## Human Assistance

Human Assistance may be called when automation, physical access, credentials, specialist craft or expert judgment creates a real blocker.

It does not:
- bypass Owner Title Gate;
- bypass Script Lock;
- bypass Production Ready Lock;
- transfer publish authority;
- become a parallel craft department;
- silently repair another department's locked work.

See:
`HUMAN_ASSISTANCE_LANE.md`

## Recovery

Application/tool success is never inferred from a command alone.

`UNKNOWN != SUCCESS`

Every state-changing application handoff requires checkpointing and postcondition verification.

See:
`STUDIO_EXECUTION_RECOVERY.md`

## Success metrics

Track:
- writing cycle time;
- owner title selection rounds;
- title revision requests;
- pre-production cycle time;
- production cycle time;
- department cycle time;
- stage cycle time;
- handoff rejection count;
- return ticket count;
- stage rework;
- program-switch violations;
- parallel-department violations;
- human assistance usage;
- quality defects;
- audience performance after publication.
