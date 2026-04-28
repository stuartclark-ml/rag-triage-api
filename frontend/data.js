/* Demo data — static, no API calls. Mirrors FastAPI output models. */

window.RAG_DATA = {
  meta: {
    incidentRef: "INC-2026-0428-117",
    analyst: "S. Clark",
    analystRole: "OHS Consultant · rag-triage-api demo",
    submittedAt: "2026-04-28T09:42:11Z",
    pipelineVersion: "rag-triage-api v0.1.0",
    modelStack: "stuSterfc/ohs-severity-classifier · map_riddor · analyse_causes · find_patterns",
  },

  narrative:
    "On the morning of 26 April 2026 at approximately 07:50, a service user (SU-431, 78yo, mod. dementia, mobility-impaired) was being assisted from bed to a wheeled commode by a single care worker (CW-12) on the second floor of Beechfield Residential. The mobile hoist normally used had been removed for sling inspection the previous evening and was not yet returned; this was not flagged at the morning handover. The care worker performed an unaided pivot transfer. The service user's left foot caught on the bedframe, both fell to the carpeted floor. The service user sustained a suspected fractured left hip and was conveyed by ambulance to North Tyneside General. The care worker reported lower-back strain but did not require hospitalisation. The room had recently been re-arranged for a deep clean; bed brakes were engaged. CCTV in the corridor confirms the timeline. SU-431's care plan flags 'two-person transfer with hoist'. The shift leader was alerted at 07:58 and the duty manager at 08:05.",

  /* ---- Severity taxonomy (C0–C4) ---- */
  severityClasses: [
    { id: 0, label: "C0", name: "None",     band: "0 days" },
    { id: 1, label: "C1", name: "Minor",    band: "1–2 days" },
    { id: 2, label: "C2", name: "Moderate", band: "3–7 days" },
    { id: 3, label: "C3", name: "Severe",   band: "8–28 days" },
    { id: 4, label: "C4", name: "Major",    band: "29+ days" },
  ],

  /* ---- T1: predict_severity ---- */
  // NOTE — integration point: live API keys probabilities by label string
  // e.g. "None (0 days)", "Minor (1-2 days)" from CLASS_LABELS in predict_severity.py.
  // Demo uses short C0-C4 keys for readability. Reconcile when wiring real endpoint.
  t1_predict_severity: {
    probabilities: {
      "C0": 0.01,
      "C1": 0.04,
      "C2": 0.12,
      "C3": 0.78,
      "C4": 0.05,
    },
    predicted_class: 3,
    confidence: 0.78,
    needlestick_flag: false,
    middle_severity_flag: true, // predicted is 2/3/4 -> high-uncertainty boundary
  },

  /* ---- T2: map_riddor ---- */
  t2_map_riddor: {
    headline: "Likely reportable — pending fracture confirmation",
    overall_status: "conditional", // reportable | conditional | not-required
    statute: "RIDDOR 2013, Schedule 1",
    categories: [
      {
        category: "Specified injury — fracture (other than fingers, thumbs, toes)",
        description:
          "A radiographically confirmed fracture of the femoral neck in a non-worker (service user) injured by a work-related activity (manual transfer) is a specified injury and reportable under Schedule 1.",
        information_needed: [
          "Radiograph result for SU-431 confirming fracture vs. contusion.",
          "Confirmation that the fall occurred in connection with work (manual handling task).",
          "Confirmation that the service user was admitted directly from the scene.",
        ],
        reporting_deadline: "Notify HSE without delay (online F2508), then submit written report within 10 days of accident.",
      },
      {
        category: "Over-7-day incapacitation (worker)",
        description:
          "If care worker CW-12 (lower-back strain) is unable to perform normal duties for more than 7 consecutive days (excluding day of accident) the incident is separately reportable.",
        information_needed: [
          "Return-to-duty date for CW-12 from occupational health.",
          "Whether modified-duties cover counts under the trust's interpretation of 'normal work'.",
        ],
        reporting_deadline: "Submit written report within 15 days of accident if threshold met.",
      },
      {
        category: "Dangerous occurrence — lifting equipment",
        description:
          "Failure or removal-from-service of a passenger or load-bearing lift can be a dangerous occurrence under Schedule 2. The hoist was withdrawn for sling inspection; verify whether this was a defect-driven withdrawal.",
        information_needed: [
          "Reason hoist was withdrawn — routine LOLER inspection vs. fault report.",
          "LOLER inspection record and last thorough examination date.",
          "Whether any other floor was affected by the same withdrawal.",
        ],
        reporting_deadline: "If a dangerous occurrence is confirmed, notify without delay; written report within 10 days.",
      },
    ],
    follow_up_questions: [
      "Confirm the radiograph result for SU-431 before submitting any RIDDOR notification.",
      "Has CW-12's back strain been triaged by occupational health, and is a return date forecast?",
      "Why was the hoist withdrawn — routine inspection or a defect? Retrieve the LOLER record.",
      "Has the care plan deviation been logged in the resident's care record within 24 hours?",
      "Is there a documented escalation pathway for missing safety-critical equipment at handover?",
    ],
  },

  /* ---- T3: analyse_causes ---- */
  t3_analyse_causes: {
    factors: [
      {
        cause_type: "Primary activity",
        description:
          "Single-handed pivot transfer of a mobility-impaired service user whose care plan specifies a two-person hoist transfer — a deviation from the documented safe system of work.",
        hsg220_section: "HSG220 §3.4 — Competence & supervision; MHOR 1992 Reg. 4(1)(b)(ii)",
        mitigation_actions: [
          "Reinforce the two-person transfer rule via mandatory toolbox talk for all care staff within 7 days.",
          "Spot-audit transfer logs weekly for 8 weeks; report exceptions to the clinical lead.",
          "Add a transfer-method confirmation prompt to the electronic care record at the point of task selection.",
        ],
      },
      {
        cause_type: "Equipment availability",
        description:
          "The mobile hoist was withdrawn the previous evening for sling inspection and was not returned to the floor before morning transfers commenced. The shortfall was not visible at handover.",
        hsg220_section: "HSG220 §5.2 — Equipment & maintenance; LOLER 1998 Reg. 9 — thorough examination",
        mitigation_actions: [
          "Replace open-loop sling inspection with a logged check-in / check-out using existing asset tags.",
          "Add a hoist-status row to the morning handover SBAR template; mandatory tick-box, no override.",
          "Provision a back-up hoist on each floor so a withdrawn unit never leaves a floor without cover.",
        ],
      },
      {
        cause_type: "Environmental factor",
        description:
          "The bedroom had been re-arranged for a deep clean; the transfer route was not re-assessed, and the service user's left foot caught on the bedframe during the pivot.",
        hsg220_section: "HSG220 §3.2 — Risk assessment; MHOR 1992 Reg. 4(1)(b)(i)",
        mitigation_actions: [
          "Trigger a 5-minute transfer-route re-assessment after any deep clean or layout change; record on the PEEP form.",
          "Mark the cleared transfer footprint on the floor in each resident's room using removable tape.",
        ],
      },
      {
        cause_type: "Communication & handover",
        description:
          "The withdrawal of the hoist was known to the night shift but not surfaced at the 07:00 handover; the morning care worker began transfers without knowledge of the equipment shortfall.",
        hsg220_section: "HSG220 §4.2 — Communication & handover",
        mitigation_actions: [
          "Mandate a closed-loop equipment-status section in the handover SBAR.",
          "Define an on-call escalation: any missing hoist or sling for more than 30 minutes escalates to the duty manager automatically.",
        ],
      },
      {
        cause_type: "Injury mechanism",
        description:
          "Low-energy fall from standing during an unaided pivot transfer of an elderly, mobility-impaired service user — the classic mechanism for fragility fractures of the proximal femur.",
        hsg220_section: "HSG220 §6.1 — Manual handling of people; HSE Manual handling assessment chart (MAC)",
        mitigation_actions: [
          "Where the assessed transfer is hoist-only, lock out manual transfer in the electronic care plan UI.",
          "Refresh staff training on falls in fragility populations — single annual module.",
        ],
      },
    ],
  },

  /* ---- T4: find_patterns ---- */
  t4_find_patterns: {
    cohort_size: 1284,
    injury_mechanism: "Low-energy fall during assisted manual transfer (hoist not used)",
    similar_incidents: [
      {
        id: "INC-2024-0883",
        narrative_excerpt:
          "Hoist withdrawn from floor overnight; not returned before AM transfers. Single carer attempted pivot; resident fell and sustained hip fracture.",
        severity_outcome: 3,
      },
      {
        id: "INC-2025-0211",
        narrative_excerpt:
          "Care plan flagged two-person transfer; CW transferred resident alone due to staff shortage. Resident fell from edge of bed; hip fracture confirmed on radiograph.",
        severity_outcome: 4,
      },
      {
        id: "INC-2024-1402",
        narrative_excerpt:
          "Sling out for inspection; staff used pivot transfer technique. Resident sustained bruising and superficial graze; no fracture.",
        severity_outcome: 1,
      },
      {
        id: "INC-2025-0577",
        narrative_excerpt:
          "Bedroom re-arranged for cleaning; transfer route obstructed by side table. Near-miss — staff aborted transfer.",
        severity_outcome: 0,
      },
      {
        id: "INC-2023-0612",
        narrative_excerpt:
          "Two-person rule deviation during shift change. Resident slipped from commode; soft-tissue injury, hospital attendance no admission.",
        severity_outcome: 2,
      },
    ],
    severity_distribution: {
      "C0": 0.04,
      "C1": 0.09,
      "C2": 0.18,
      "C3": 0.55,
      "C4": 0.14,
    },
  },
};
